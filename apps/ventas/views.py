import json
from datetime import datetime
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, F, Sum
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db import transaction

from .models import NotaVenta, DetalleVenta
from apps.clientes.models import Cliente
from apps.inventario.models import Inventario, Producto
from apps.personal.models import Empleado


@login_required
def lista(request):
    q = request.GET.get('q', '').strip()
    qs = NotaVenta.objects.select_related('cliente__persona', 'empleado__persona')
    if q:
        qs = qs.filter(
            Q(cliente__persona__nombre__icontains=q) |
            Q(cliente__nit__icontains=q) |
            Q(id__icontains=q)
        )
    page = Paginator(qs.order_by('-fecha', '-hora'), 20).get_page(request.GET.get('page'))
    total_mes = qs.aggregate(t=Sum('monto_total'))['t'] or 0
    return render(request, 'ventas/lista.html', {
        'ventas': page, 'q': q, 'total_mes': total_mes,
    })


@login_required
def detalle(request, pk):
    venta = get_object_or_404(
        NotaVenta.objects.select_related('cliente__persona', 'empleado__persona'),
        pk=pk
    )
    detalles = venta.detalles.select_related('inventario__producto').all()
    return render(request, 'ventas/detalle.html', {'venta': venta, 'detalles': detalles})


@login_required
def pos(request):
    """Punto de venta. La interfaz es JS, esta vista renderea el shell."""
    clientes = Cliente.objects.select_related('persona').all()
    # Productos con stock disponible
    productos = (Producto.objects
                 .filter(activo=True, lotes__cantidad_disponible__gt=0)
                 .distinct())
    return render(request, 'ventas/pos.html', {
        'clientes': clientes,
        'productos': productos,
    })


@login_required
def api_productos_disponibles(request):
    """API JSON para el POS: productos con stock."""
    q = request.GET.get('q', '').strip()
    qs = Producto.objects.filter(activo=True)
    if q:
        qs = qs.filter(Q(nombre__icontains=q) | Q(codigo__icontains=q))

    data = []
    for p in qs[:50]:
        stock = p.stock_total
        if stock > 0:
            # Tomamos el lote mas viejo (FIFO)
            lote = p.lotes.filter(cantidad_disponible__gt=0).order_by('fecha_adquision').first()
            data.append({
                'id': p.id,
                'codigo': p.codigo,
                'nombre': p.nombre,
                'categoria': p.categoria,
                'precio': float(p.precio_venta),
                'stock': stock,
                'lote_id': lote.id if lote else None,
                'imagen': p.imagen.url if p.imagen else '',
            })
    return JsonResponse({'productos': data})


@login_required
@transaction.atomic
def pos_confirmar(request):
    """Procesa una venta desde el POS."""
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'Metodo no permitido'}, status=405)

    try:
        payload = json.loads(request.body.decode('utf-8'))
        cliente_id = payload.get('cliente_id')
        items = payload.get('items', [])

        if not cliente_id:
            return JsonResponse({'ok': False, 'error': 'Cliente requerido'}, status=400)
        if not items:
            return JsonResponse({'ok': False, 'error': 'Carrito vacio'}, status=400)

        cliente = Cliente.objects.get(pk=cliente_id)
        # Empleado vinculado al user, sino el primero
        empleado = None
        try:
            from apps.personal.models import Login
            login_obj = Login.objects.filter(user=request.user).first()
            if login_obj:
                empleado = login_obj.empleado
        except Exception:
            pass
        if not empleado:
            empleado = Empleado.objects.first()
        if not empleado:
            return JsonResponse({'ok': False, 'error': 'No hay empleados registrados'}, status=400)

        ahora = datetime.now()
        venta = NotaVenta.objects.create(
            fecha=ahora.date(),
            hora=ahora.time().replace(microsecond=0),
            monto_total=0,
            moneda='BOB',
            tipo_cambio=1,
            cliente=cliente,
            empleado=empleado,
        )

        for it in items:
            producto = Producto.objects.get(pk=it['producto_id'])
            cantidad_pedida = int(it['cantidad'])
            precio = Decimal(str(it.get('precio') or producto.precio_venta))

            # Asignar a lotes con FIFO
            restante = cantidad_pedida
            lotes = (Inventario.objects
                     .filter(producto=producto, cantidad_disponible__gt=0)
                     .order_by('fecha_adquision'))
            for lote in lotes:
                if restante <= 0:
                    break
                tomar = min(restante, lote.cantidad_disponible)
                DetalleVenta.objects.create(
                    concepto=producto.nombre,
                    cantidad=tomar,
                    precio=precio,
                    nota_venta=venta,
                    inventario=lote,
                )
                restante -= tomar

            if restante > 0:
                raise ValueError(f"Stock insuficiente para {producto.nombre}")

        venta.calcular_total()

        return JsonResponse({
            'ok': True,
            'venta_id': venta.id,
            'total': float(venta.monto_total),
        })

    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)
