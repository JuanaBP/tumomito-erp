from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Proveedor
from .forms import ProveedorForm


@login_required
def lista(request):
    q = request.GET.get('q', '').strip()
    qs = Proveedor.objects.all()
    if q:
        qs = qs.filter(
            Q(empresa__icontains=q) | Q(nit__icontains=q) |
            Q(representante_legal__icontains=q) | Q(pais__icontains=q)
        )
    page = Paginator(qs, 15).get_page(request.GET.get('page'))
    return render(request, 'proveedores/lista.html', {'proveedores': page, 'q': q})


@login_required
def crear(request):
    form = ProveedorForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Proveedor creado.')
        return redirect('proveedores:lista')
    return render(request, 'proveedores/form.html', {'form': form, 'titulo': 'Nuevo Proveedor'})


@login_required
def editar(request, pk):
    obj = get_object_or_404(Proveedor, pk=pk)
    form = ProveedorForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        messages.success(request, 'Proveedor actualizado.')
        return redirect('proveedores:lista')
    return render(request, 'proveedores/form.html', {'form': form, 'titulo': 'Editar Proveedor'})


@login_required
def eliminar(request, pk):
    obj = get_object_or_404(Proveedor, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Proveedor eliminado.')
        return redirect('proveedores:lista')
    return render(request, 'proveedores/confirmar_eliminar.html', {'proveedor': obj})


@login_required
def detalle(request, pk):
    obj = get_object_or_404(Proveedor, pk=pk)
    compras = obj.notacompra_set.order_by('-fecha')[:10] if hasattr(obj, 'notacompra_set') else []
    return render(request, 'proveedores/detalle.html', {'proveedor': obj, 'compras': compras})
