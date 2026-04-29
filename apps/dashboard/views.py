from datetime import date, timedelta
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Sum, Count, F, DecimalField
from django.db.models.functions import TruncMonth, TruncDay

from apps.ventas.models import NotaVenta, DetalleVenta
from apps.compras.models import NotaCompra
from apps.inventario.models import Producto, Inventario
from apps.clientes.models import Cliente
from apps.proveedores.models import Proveedor


@login_required
def home(request):
    hoy = date.today()
    inicio_mes = hoy.replace(day=1)
    hace_30 = hoy - timedelta(days=30)

    # KPIs principales
    ventas_hoy = NotaVenta.objects.filter(fecha=hoy).aggregate(
        total=Sum('monto_total'), n=Count('id')
    )
    ventas_mes = NotaVenta.objects.filter(fecha__gte=inicio_mes).aggregate(
        total=Sum('monto_total'), n=Count('id')
    )
    compras_mes = NotaCompra.objects.filter(fecha__gte=inicio_mes).aggregate(
        total=Sum('monto_total')
    )

    # Stock total y productos con stock bajo
    productos_total = Producto.objects.filter(activo=True).count()
    stock_bajo = []
    for p in Producto.objects.filter(activo=True):
        if p.stock_total < 10:
            stock_bajo.append(p)
    stock_bajo = stock_bajo[:5]

    # Ultimas ventas
    ultimas_ventas = NotaVenta.objects.select_related('cliente__persona', 'empleado__persona') \
        .order_by('-fecha', '-hora')[:5]

    # Top productos vendidos (ultimo mes)
    top_productos = (DetalleVenta.objects
                     .filter(nota_venta__fecha__gte=hace_30)
                     .values('inventario__producto__nombre')
                     .annotate(total_vendido=Sum('cantidad'),
                               ingresos=Sum(F('cantidad') * F('precio'),
                                            output_field=DecimalField()))
                     .order_by('-total_vendido')[:5])

    # Ventas por dia (ultimo mes) para el grafico
    ventas_por_dia = (NotaVenta.objects
                      .filter(fecha__gte=hace_30)
                      .annotate(dia=TruncDay('fecha'))
                      .values('dia')
                      .annotate(total=Sum('monto_total'))
                      .order_by('dia'))

    chart_labels = [v['dia'].strftime('%d/%m') for v in ventas_por_dia]
    chart_values = [float(v['total'] or 0) for v in ventas_por_dia]

    # Ventas por categoria
    ventas_categoria = (DetalleVenta.objects
                        .filter(nota_venta__fecha__gte=hace_30)
                        .values('inventario__producto__categoria')
                        .annotate(total=Sum(F('cantidad') * F('precio'),
                                            output_field=DecimalField()))
                        .order_by('-total'))

    cat_labels = [v['inventario__producto__categoria'] for v in ventas_categoria]
    cat_values = [float(v['total'] or 0) for v in ventas_categoria]

    contexto = {
        'ventas_hoy_total': ventas_hoy['total'] or 0,
        'ventas_hoy_n': ventas_hoy['n'] or 0,
        'ventas_mes_total': ventas_mes['total'] or 0,
        'ventas_mes_n': ventas_mes['n'] or 0,
        'compras_mes_total': compras_mes['total'] or 0,
        'productos_total': productos_total,
        'clientes_total': Cliente.objects.count(),
        'proveedores_total': Proveedor.objects.filter(activo=True).count(),
        'stock_bajo': stock_bajo,
        'ultimas_ventas': ultimas_ventas,
        'top_productos': top_productos,
        'chart_labels': chart_labels,
        'chart_values': chart_values,
        'cat_labels': cat_labels,
        'cat_values': cat_values,
    }
    return render(request, 'dashboard/home.html', contexto)
