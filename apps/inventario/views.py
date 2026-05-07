from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Sum
from django.core.paginator import Paginator

from apps.personal.permissions import requires_module
from .models import Producto, Inventario, Categoria
from .forms import ProductoForm, InventarioForm, CategoriaForm


# ==========================================================
# CATEGORIAS - CRUD
# ==========================================================
@requires_module('categorias')
def categorias_lista(request):
    qs = Categoria.objects.all()
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(nombre__icontains=q) | Q(descripcion__icontains=q))
    return render(request, 'categorias/lista.html', {
        'categorias': qs,
        'q': q,
    })


@requires_module('categorias')
def categoria_crear(request):
    form = CategoriaForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Categoria creada correctamente.')
        return redirect('inventario:categorias')
    return render(request, 'categorias/form.html', {
        'form': form,
        'titulo': 'Nueva Categoria',
    })


@requires_module('categorias')
def categoria_editar(request, pk):
    obj = get_object_or_404(Categoria, pk=pk)
    form = CategoriaForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        messages.success(request, 'Categoria actualizada.')
        return redirect('inventario:categorias')
    return render(request, 'categorias/form.html', {
        'form': form,
        'titulo': f'Editar: {obj.nombre}',
        'categoria': obj,
    })


@requires_module('categorias')
def categoria_eliminar(request, pk):
    obj = get_object_or_404(Categoria, pk=pk)
    productos_usando = obj.productos.count()
    if request.method == 'POST':
        if productos_usando > 0:
            messages.error(request,
                f'No se puede eliminar: {productos_usando} producto(s) usan esta categoria. '
                f'Desactivala en lugar de eliminar.')
            return redirect('inventario:categorias')
        obj.delete()
        messages.success(request, 'Categoria eliminada.')
        return redirect('inventario:categorias')
    return render(request, 'categorias/confirmar_eliminar.html', {
        'categoria': obj,
        'productos_usando': productos_usando,
    })


# ==========================================================
# PRODUCTOS - CRUD
# ==========================================================
@requires_module('productos')
def productos_lista(request):
    q = request.GET.get('q', '').strip()
    cat_id = request.GET.get('categoria', '').strip()
    qs = Producto.objects.select_related('categoria').all()
    if q:
        qs = qs.filter(
            Q(codigo__icontains=q) | Q(nombre__icontains=q) |
            Q(fabricante__icontains=q) | Q(subcategoria__icontains=q)
        )
    if cat_id:
        qs = qs.filter(categoria_id=cat_id)
    page = Paginator(qs, 20).get_page(request.GET.get('page'))
    return render(request, 'productos/lista.html', {
        'productos': page,
        'q': q,
        'cat_id': cat_id,
        'categorias': Categoria.objects.filter(activo=True),
    })


@requires_module('productos')
def producto_crear(request):
    form = ProductoForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Producto creado.')
        return redirect('inventario:productos')
    return render(request, 'productos/form.html', {'form': form, 'titulo': 'Nuevo Producto'})


@requires_module('productos')
def producto_editar(request, pk):
    obj = get_object_or_404(Producto, pk=pk)
    form = ProductoForm(request.POST or None, request.FILES or None, instance=obj)
    if form.is_valid():
        form.save()
        messages.success(request, 'Producto actualizado.')
        return redirect('inventario:productos')
    return render(request, 'productos/form.html', {'form': form, 'titulo': 'Editar Producto'})


@requires_module('productos')
def producto_detalle(request, pk):
    obj = get_object_or_404(Producto, pk=pk)
    lotes = obj.lotes.order_by('fecha_adquision')
    return render(request, 'productos/detalle.html', {'producto': obj, 'lotes': lotes})


@requires_module('productos')
def producto_eliminar(request, pk):
    obj = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        try:
            obj.delete()
            messages.success(request, 'Producto eliminado.')
        except Exception:
            obj.activo = False
            obj.save()
            messages.warning(request, 'Producto desactivado (tenia historial).')
        return redirect('inventario:productos')
    return render(request, 'productos/confirmar_eliminar.html', {'producto': obj})


# ==========================================================
# INVENTARIO (LOTES)
# ==========================================================
@requires_module('inventario')
def inventario_lista(request):
    q = request.GET.get('q', '').strip()
    qs = Inventario.objects.select_related('producto').all()
    if q:
        qs = qs.filter(
            Q(nro_lote__icontains=q) | Q(producto__nombre__icontains=q) |
            Q(producto__codigo__icontains=q)
        )
    page = Paginator(qs, 25).get_page(request.GET.get('page'))

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


@requires_module('inventario')
def inventario_crear(request):
    form = InventarioForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Lote registrado en inventario.')
        return redirect('inventario:lotes')
    return render(request, 'inventario/form.html', {'form': form, 'titulo': 'Nuevo Lote'})


@requires_module('inventario')
def inventario_editar(request, pk):
    obj = get_object_or_404(Inventario, pk=pk)
    form = InventarioForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        messages.success(request, 'Lote actualizado.')
        return redirect('inventario:lotes')
    return render(request, 'inventario/form.html', {
        'form': form, 'titulo': f'Editar Lote {obj.nro_lote}'
    })
