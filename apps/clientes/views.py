from django.shortcuts import render, redirect, get_object_or_404
from apps.personal.permissions import requires_module
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Cliente
from .forms import ClienteForm


@requires_module('clientes')
def lista(request):
    q = request.GET.get('q', '').strip()
    qs = Cliente.objects.select_related('persona').all()
    if q:
        qs = qs.filter(
            Q(persona__nombre__icontains=q) |
            Q(persona__ci__icontains=q) |
            Q(nit__icontains=q) |
            Q(razon_social__icontains=q)
        )
    paginator = Paginator(qs, 15)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'clientes/lista.html', {'clientes': page, 'q': q})


@requires_module('clientes')
def crear(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente creado exitosamente.')
            return redirect('clientes:lista')
    else:
        form = ClienteForm()
    return render(request, 'clientes/form.html', {'form': form, 'titulo': 'Nuevo Cliente'})


@requires_module('clientes')
def editar(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente actualizado.')
            return redirect('clientes:lista')
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'clientes/form.html', {'form': form, 'titulo': 'Editar Cliente'})


@requires_module('clientes')
def eliminar(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        cliente.persona.delete()  # cascade elimina cliente
        messages.success(request, 'Cliente eliminado.')
        return redirect('clientes:lista')
    return render(request, 'clientes/confirmar_eliminar.html', {'cliente': cliente})


@requires_module('clientes')
def detalle(request, pk):
    cliente = get_object_or_404(Cliente.objects.select_related('persona'), pk=pk)
    ventas = cliente.notaventa_set.order_by('-fecha')[:10] if hasattr(cliente, 'notaventa_set') else []
    return render(request, 'clientes/detalle.html', {'cliente': cliente, 'ventas': ventas})
