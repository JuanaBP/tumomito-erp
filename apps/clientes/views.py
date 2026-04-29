from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Cliente
from .forms import ClienteForm


@login_required
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


@login_required
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


@login_required
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


@login_required
def eliminar(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        cliente.persona.delete()  # cascade elimina cliente
        messages.success(request, 'Cliente eliminado.')
        return redirect('clientes:lista')
    return render(request, 'clientes/confirmar_eliminar.html', {'cliente': cliente})


@login_required
def detalle(request, pk):
    cliente = get_object_or_404(Cliente.objects.select_related('persona'), pk=pk)
    ventas = cliente.notaventa_set.order_by('-fecha')[:10] if hasattr(cliente, 'notaventa_set') else []
    return render(request, 'clientes/detalle.html', {'cliente': cliente, 'ventas': ventas})
