import json
from datetime import datetime
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from apps.personal.permissions import requires_module
from django.contrib import messages
from django.db.models import Q, Sum
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db import transaction

from .models import NotaCompra, DetalleCompra
from apps.proveedores.models import Proveedor
from apps.inventario.models import Producto, Inventario
from apps.personal.models import Empleado, Login


@requires_module('compras')
def lista(request):
    q = request.GET.get('q', '').strip()
    qs = NotaCompra.objects.select_related('proveedor', 'empleado__persona')
    if q:
        qs = qs.filter(
            Q(proveedor__empresa__icontains=q) |
            Q(proveedor__nit__icontains=q) | Q(id__icontains=q)
        )
    page = Paginator(qs.order_by('-fecha', '-hora'), 20).get_page(request.GET.get('page'))
    total = qs.aggregate(t=Sum('monto_total'))['t'] or 0
    return render(request, 'compras/lista.html', {'compras': page, 'q': q, 'total': total})


@requires_module('compras')
def detalle(request, pk):
    compra = get_object_or_404(
        NotaCompra.objects.select_related('proveedor', 'empleado__persona'),
        pk=pk
    )
    detalles = compra.detalles.select_related('producto').all()
    return render(request, 'compras/detalle.html', {'compra': compra, 'detalles': detalles})


@requires_module('compras')
def nueva(request):
    """Vista para crear una nueva orden de compra (formulario interactivo)."""
    proveedores = Proveedor.objects.filter(activo=True)
    productos = Producto.objects.filter(activo=True)
    return render(request, 'compras/nueva.html', {
        'proveedores': proveedores,
        'productos': productos,
    })


@requires_module('compras')
@transaction.atomic
def confirmar(request):
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'Metodo no permitido'}, status=405)

    try:
        payload = json.loads(request.body.decode('utf-8'))
        proveedor_id = payload.get('proveedor_id')
        moneda = payload.get('moneda', 'BOB')
        tipo_cambio = Decimal(str(payload.get('tipo_cambio', 1)))
        items = payload.get('items', [])

        if not proveedor_id or not items:
            return JsonResponse({'ok': False, 'error': 'Faltan datos'}, status=400)

        proveedor = Proveedor.objects.get(pk=proveedor_id)

        empleado = None
        login_obj = Login.objects.filter(user=request.user).first()
        if login_obj:
            empleado = login_obj.empleado
        if not empleado:
            empleado = Empleado.objects.first()
        if not empleado:
            return JsonResponse({'ok': False, 'error': 'No hay empleados'}, status=400)

        ahora = datetime.now()
        compra = NotaCompra.objects.create(
            fecha=ahora.date(),
            hora=ahora.time().replace(microsecond=0),
            monto_total=0,
            moneda=moneda,
            tipo_cambio=tipo_cambio,
            proveedor=proveedor,
            empleado=empleado,
        )

        for it in items:
            producto = Producto.objects.get(pk=it['producto_id'])
            cantidad = int(it['cantidad'])
            precio = Decimal(str(it['precio']))

            detalle = DetalleCompra.objects.create(
                concepto=producto.nombre,
                cantidad=cantidad,
                precio=precio,
                nota_compra=compra,
                producto=producto,
            )

            # Crear lote de inventario automaticamente
            Inventario.objects.create(
                nro_lote=f"LOTE-{compra.id}-{detalle.id}",
                cantidad_recibida=cantidad,
                cantidad_disponible=cantidad,
                fecha_adquision=ahora.date(),
                coste_unitario=precio,
                coste_final=precio * cantidad,
                producto=producto,
                detalle_compra=detalle,
            )

        compra.calcular_total()

        return JsonResponse({'ok': True, 'compra_id': compra.id, 'total': float(compra.monto_total)})

    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)
