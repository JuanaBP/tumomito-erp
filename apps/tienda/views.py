from datetime import datetime
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Sum
from django.http import JsonResponse, HttpResponseForbidden
from django.core.paginator import Paginator

from apps.inventario.models import Producto, Inventario
from apps.clientes.models import Cliente
from apps.core.models import Persona
from apps.ventas.models import NotaVenta, DetalleVenta
from apps.personal.models import Empleado

from .models import Pedido, DetallePedido, Direccion
from .cart import Carrito


# =========================================================
# TIENDA PUBLICA
# =========================================================

def home(request):
    destacados = Producto.objects.filter(activo=True, visible_tienda=True, destacado=True)[:8]
    nuevos = Producto.objects.filter(activo=True, visible_tienda=True).order_by('-creado')[:8]
    categorias = Producto.objects.filter(activo=True, visible_tienda=True) \
        .values_list('categoria', flat=True).distinct()
    return render(request, 'tienda/home.html', {
        'destacados': destacados,
        'nuevos': nuevos,
        'categorias': categorias,
        'carrito': Carrito(request),
    })


def catalogo(request):
    qs = Producto.objects.filter(activo=True, visible_tienda=True)
    cat = request.GET.get('categoria', '').strip()
    q = request.GET.get('q', '').strip()
    orden = request.GET.get('orden', 'nombre')

    if cat:
        qs = qs.filter(categoria=cat)
    if q:
        qs = qs.filter(Q(nombre__icontains=q) | Q(descripcion__icontains=q) | Q(fabricante__icontains=q))

    if orden == 'precio_asc':
        qs = qs.order_by('precio_venta')
    elif orden == 'precio_desc':
        qs = qs.order_by('-precio_venta')
    elif orden == 'nuevos':
        qs = qs.order_by('-creado')
    else:
        qs = qs.order_by('nombre')

    page = Paginator(qs, 12).get_page(request.GET.get('page'))

    categorias = Producto.objects.filter(activo=True, visible_tienda=True) \
        .values_list('categoria', flat=True).distinct()

    cliente = None
    if request.user.is_authenticated:
        cliente = getattr(request.user, 'cliente_perfil', None)

    return render(request, 'tienda/catalogo.html', {
        'productos': page,
        'categorias': categorias,
        'cat': cat,
        'q': q,
        'orden': orden,
        'cliente': cliente,
        'carrito': Carrito(request),
    })


def detalle_producto(request, slug):
    producto = get_object_or_404(Producto, slug=slug, activo=True, visible_tienda=True)
    relacionados = Producto.objects.filter(
        categoria=producto.categoria, activo=True, visible_tienda=True
    ).exclude(id=producto.id)[:4]
    cliente = None
    if request.user.is_authenticated:
        cliente = getattr(request.user, 'cliente_perfil', None)
    return render(request, 'tienda/producto.html', {
        'producto': producto,
        'relacionados': relacionados,
        'cliente': cliente,
        'carrito': Carrito(request),
    })


# =========================================================
# CARRITO
# =========================================================

def carrito_ver(request):
    return render(request, 'tienda/carrito.html', {'carrito': Carrito(request)})


def carrito_agregar(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id, activo=True, visible_tienda=True)
    cantidad = int(request.POST.get('cantidad', 1)) if request.method == 'POST' else 1
    sumar = request.POST.get('sumar', '1') == '1'
    Carrito(request).agregar(producto, cantidad, sumar)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        c = Carrito(request)
        return JsonResponse({'ok': True, 'total_items': c.total_items, 'total': float(c.total)})
    messages.success(request, f'{producto.nombre} agregado al carrito.')
    return redirect(request.META.get('HTTP_REFERER', 'tienda:catalogo'))


def carrito_eliminar(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    Carrito(request).eliminar(producto)
    return redirect('tienda:carrito')


def carrito_vaciar(request):
    Carrito(request).vaciar()
    return redirect('tienda:carrito')


# =========================================================
# REGISTRO Y LOGIN DE CLIENTES
# =========================================================

def registro(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        nombre = request.POST.get('nombre', '').strip()
        ci = request.POST.get('ci', '').strip()
        nit = request.POST.get('nit', '').strip()
        email = request.POST.get('email', '').strip()
        celular = request.POST.get('celular', '').strip()

        errores = []
        if not all([username, password, nombre, ci, nit, celular]):
            errores.append('Completa todos los campos obligatorios.')
        if password != password2:
            errores.append('Las contrasenas no coinciden.')
        if len(password) < 6:
            errores.append('La contrasena debe tener minimo 6 caracteres.')
        if User.objects.filter(username=username).exists():
            errores.append('Ese nombre de usuario ya existe.')
        if Persona.objects.filter(ci=ci).exists():
            errores.append('Ya existe una persona con ese CI.')

        if errores:
            for e in errores:
                messages.error(request, e)
        else:
            user = User.objects.create_user(username=username, password=password,
                                            email=email, first_name=nombre.split()[0])
            persona = Persona.objects.create(
                nombre=nombre, fecha_nacimiento='2000-01-01', ci=ci,
                nacionalidad='Boliviana', celular=celular, email=email,
            )
            Cliente.objects.create(persona=persona, nit=nit, tipo='minorista', user=user)
            user_auth = authenticate(username=username, password=password)
            if user_auth:
                login(request, user_auth)
            messages.success(request, f'Bienvenido {nombre}! Tu cuenta fue creada.')
            return redirect('tienda:home')

    return render(request, 'tienda/registro.html')


def login_cliente(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect(request.GET.get('next') or 'tienda:home')
        messages.error(request, 'Usuario o contrasena incorrectos.')
    return render(request, 'tienda/login.html')


# =========================================================
# CHECKOUT Y PEDIDO
# =========================================================

@login_required(login_url='tienda:login')
def checkout(request):
    cliente = getattr(request.user, 'cliente_perfil', None)
    if not cliente:
        messages.error(request, 'Tu cuenta no tiene perfil de cliente.')
        return redirect('tienda:home')

    carrito = Carrito(request)
    if len(carrito) == 0:
        messages.warning(request, 'Tu carrito esta vacio.')
        return redirect('tienda:catalogo')

    direcciones = cliente.direcciones.all()

    if request.method == 'POST':
        metodo_pago = request.POST.get('metodo_pago')
        direccion_id = request.POST.get('direccion_id')
        observaciones = request.POST.get('observaciones', '')

        if not metodo_pago or not direccion_id:
            messages.error(request, 'Selecciona metodo de pago y direccion.')
        else:
            direccion = get_object_or_404(Direccion, id=direccion_id, cliente=cliente)
            with transaction.atomic():
                pedido = Pedido.objects.create(
                    cliente=cliente,
                    direccion=direccion,
                    metodo_pago=metodo_pago,
                    monto_envio=Decimal('15.00'),
                    observaciones=observaciones,
                )
                for item in carrito.items():
                    DetallePedido.objects.create(
                        pedido=pedido,
                        producto=item['producto'],
                        cantidad=item['cantidad'],
                        precio_unitario=item['precio_unitario'],
                        es_mayorista=item['es_mayorista'],
                    )
                pedido.calcular_totales()
                carrito.vaciar()
            return redirect('tienda:pedido_pago', pk=pedido.id)

    return render(request, 'tienda/checkout.html', {
        'carrito': carrito,
        'direcciones': direcciones,
        'cliente': cliente,
    })


@login_required(login_url='tienda:login')
def direccion_nueva(request):
    cliente = getattr(request.user, 'cliente_perfil', None)
    if not cliente:
        return redirect('tienda:home')
    if request.method == 'POST':
        Direccion.objects.create(
            cliente=cliente,
            alias=request.POST.get('alias', 'Casa'),
            ciudad=request.POST.get('ciudad', 'Santa Cruz'),
            zona=request.POST.get('zona', ''),
            calle=request.POST.get('calle', ''),
            numero=request.POST.get('numero', ''),
            referencia=request.POST.get('referencia', ''),
            telefono=request.POST.get('telefono', cliente.persona.celular),
            es_principal=not cliente.direcciones.exists(),
        )
        return redirect('tienda:checkout')
    return render(request, 'tienda/direccion_form.html')


@login_required(login_url='tienda:login')
def pedido_pago(request, pk):
    cliente = getattr(request.user, 'cliente_perfil', None)
    pedido = get_object_or_404(Pedido, pk=pk, cliente=cliente)

    if request.method == 'POST' and pedido.estado == 'pendiente':
        if pedido.metodo_pago in ('transferencia', 'qr'):
            comp = request.FILES.get('comprobante')
            ref = request.POST.get('referencia_pago', '')
            if comp:
                pedido.comprobante_pago = comp
                pedido.referencia_pago = ref
                pedido.estado = 'pagado'
                pedido.save()
                messages.success(request, 'Comprobante enviado. Validaremos tu pago a la brevedad.')
                return redirect('tienda:mis_pedidos')
            else:
                messages.error(request, 'Debes adjuntar el comprobante.')
        else:
            pedido.estado = 'pagado'
            pedido.save()
            messages.success(request, 'Pedido confirmado. Pagaras al recibir.')
            return redirect('tienda:mis_pedidos')

    return render(request, 'tienda/pedido_pago.html', {'pedido': pedido})


@login_required(login_url='tienda:login')
def mis_pedidos(request):
    cliente = getattr(request.user, 'cliente_perfil', None)
    if not cliente:
        return redirect('tienda:home')
    pedidos = cliente.pedidos.all()
    return render(request, 'tienda/mis_pedidos.html', {'pedidos': pedidos})


@login_required(login_url='tienda:login')
def mi_pedido_detalle(request, pk):
    cliente = getattr(request.user, 'cliente_perfil', None)
    pedido = get_object_or_404(Pedido, pk=pk, cliente=cliente)
    return render(request, 'tienda/mi_pedido_detalle.html', {'pedido': pedido})


# =========================================================
# ADMIN DE PEDIDOS ONLINE (DESDE ERP)
# =========================================================

@login_required(login_url='login')
def admin_pedidos(request):
    if not request.user.is_staff:
        return HttpResponseForbidden()
    estado = request.GET.get('estado', '').strip()
    qs = Pedido.objects.select_related('cliente__persona').all()
    if estado:
        qs = qs.filter(estado=estado)
    page = Paginator(qs, 20).get_page(request.GET.get('page'))

    resumen = {
        'pendientes': Pedido.objects.filter(estado='pendiente').count(),
        'pagados': Pedido.objects.filter(estado='pagado').count(),
        'preparando': Pedido.objects.filter(estado__in=['confirmado', 'preparando']).count(),
        'enviados': Pedido.objects.filter(estado='enviado').count(),
    }
    return render(request, 'tienda/admin_pedidos.html', {
        'pedidos': page,
        'estado': estado,
        'resumen': resumen,
        'estados': Pedido.ESTADOS,
    })


@login_required(login_url='login')
def admin_pedido_detalle(request, pk):
    if not request.user.is_staff:
        return HttpResponseForbidden()
    pedido = get_object_or_404(Pedido, pk=pk)
    return render(request, 'tienda/admin_pedido_detalle.html', {'pedido': pedido})


@login_required(login_url='login')
@transaction.atomic
def admin_pedido_confirmar(request, pk):
    """Confirma el pago: crea NotaVenta, descuenta inventario por FIFO."""
    if not request.user.is_staff:
        return HttpResponseForbidden()

    pedido = get_object_or_404(Pedido, pk=pk)
    if pedido.estado not in ('pagado', 'pendiente'):
        messages.warning(request, 'Este pedido ya fue procesado.')
        return redirect('tienda:admin_pedido_detalle', pk=pk)

    # Empleado del usuario actual o el primero
    empleado = None
    try:
        from apps.personal.models import Login as LoginModel
        login_obj = LoginModel.objects.filter(user=request.user).first()
        if login_obj:
            empleado = login_obj.empleado
    except Exception:
        pass
    if not empleado:
        empleado = Empleado.objects.first()
    if not empleado:
        messages.error(request, 'No hay empleados registrados.')
        return redirect('tienda:admin_pedido_detalle', pk=pk)

    # Crear NotaVenta
    ahora = datetime.now()
    venta = NotaVenta.objects.create(
        fecha=ahora.date(),
        hora=ahora.time().replace(microsecond=0),
        monto_total=0, moneda='BOB', tipo_cambio=1,
        cliente=pedido.cliente, empleado=empleado,
    )

    # Descontar inventario por FIFO
    try:
        for d in pedido.detalles.all():
            restante = d.cantidad
            lotes = (Inventario.objects
                     .filter(producto=d.producto, cantidad_disponible__gt=0)
                     .order_by('fecha_adquision'))
            for lote in lotes:
                if restante <= 0:
                    break
                tomar = min(restante, lote.cantidad_disponible)
                DetalleVenta.objects.create(
                    concepto=d.producto.nombre, cantidad=tomar,
                    precio=d.precio_unitario,
                    nota_venta=venta, inventario=lote,
                )
                restante -= tomar
            if restante > 0:
                raise ValueError(f'Stock insuficiente para {d.producto.nombre}')
        venta.calcular_total()
        pedido.nota_venta = venta
        pedido.estado = 'confirmado'
        pedido.save()
        messages.success(request, f'Pedido confirmado. Se genero la nota de venta NV-{venta.id:06d}.')
    except Exception as e:
        transaction.set_rollback(True)
        messages.error(request, f'Error: {e}')

    return redirect('tienda:admin_pedido_detalle', pk=pk)


@login_required(login_url='login')
def admin_pedido_estado(request, pk):
    """Cambiar estado del pedido (preparando/enviado/entregado/cancelado)."""
    if not request.user.is_staff:
        return HttpResponseForbidden()
    pedido = get_object_or_404(Pedido, pk=pk)
    nuevo = request.POST.get('estado')
    if nuevo in dict(Pedido.ESTADOS):
        pedido.estado = nuevo
        if nuevo == 'entregado':
            pedido.fecha_entrega = datetime.now()
        pedido.save()
        messages.success(request, f'Estado actualizado a "{pedido.get_estado_display()}".')
    return redirect('tienda:admin_pedido_detalle', pk=pk)
