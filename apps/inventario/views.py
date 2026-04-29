from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum
from django.core.paginator import Paginator
from .models import Producto, Inventario
from .forms import ProductoForm, InventarioForm


# ---------- PRODUCTOS ----------
@login_required
def productos_lista(request):
    q = request.GET.get('q', '').strip()
    cat = request.GET.get('categoria', '').strip()
    qs = Producto.objects.all()
    if q:
        qs = qs.filter(
            Q(codigo__icontains=q) | Q(nombre__icontains=q) |
            Q(fabricante__icontains=q) | Q(subcategoria__icontains=q)
        )
    if cat:
        qs = qs.filter(categoria=cat)
    page = Paginator(qs, 20).get_page(request.GET.get('page'))
    return render(request, 'productos/lista.html', {
        'productos': page,
        'q': q,
        'cat': cat,
        'categorias': Producto.CATEGORIA_CHOICES,
    })


@login_required
def producto_crear(request):
    form = ProductoForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Producto creado.')
        return redirect('inventario:productos')
    return render(request, 'productos/form.html', {'form': form, 'titulo': 'Nuevo Producto'})


@login_required
def producto_editar(request, pk):
    obj = get_object_or_404(Producto, pk=pk)
    form = ProductoForm(request.POST or None, request.FILES or None, instance=obj)
    if form.is_valid():
        form.save()
        messages.success(request, 'Producto actualizado.')
        return redirect('inventario:productos')
    return render(request, 'productos/form.html', {'form': form, 'titulo': 'Editar Producto'})


@login_required
def producto_detalle(request, pk):
    obj = get_object_or_404(Producto, pk=pk)
    lotes = obj.lotes.order_by('fecha_adquision')
    return render(request, 'productos/detalle.html', {'producto': obj, 'lotes': lotes})


@login_required
def producto_eliminar(request, pk):
    obj = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Producto eliminado.')
        return redirect('inventario:productos')
    return render(request, 'productos/confirmar_eliminar.html', {'producto': obj})


# ---------- INVENTARIO (LOTES) ----------
@login_required
def inventario_lista(request):
    q = request.GET.get('q', '').strip()
    qs = Inventario.objects.select_related('producto').all()
    if q:
        qs = qs.filter(
            Q(nro_lote__icontains=q) | Q(producto__nombre__icontains=q) |
            Q(producto__codigo__icontains=q)
        )
    page = Paginator(qs, 25).get_page(request.GET.get('page'))

    # Resumen
    total_unidades = Inventario.objects.aggregate(t=Sum('cantidad_disponible'))['t'] or 0
    valor_inventario = sum(
        l.cantidad_disponible * l.coste_unitario for l in Inventario.objects.all()
    )

    return render(request, 'inventario/lista.html', {
        'lotes': page,
        'q': q,
        'total_unidades': total_unidades,
        'valor_inventario': valor_inventario,
    })


@login_required
def inventario_crear(request):
    form = InventarioForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Lote registrado en inventario.')
        return redirect('inventario:lotes')
    return render(request, 'inventario/form.html', {'form': form, 'titulo': 'Nuevo Lote'})


@login_required
def inventario_editar(request, pk):
    obj = get_object_or_404(Inventario, pk=pk)
    form = InventarioForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        messages.success(request, 'Lote actualizado.')
        return redirect('inventario:lotes')
    return render(request, 'inventario/form.html', {'form': form, 'titulo': 'Editar Lote'})
