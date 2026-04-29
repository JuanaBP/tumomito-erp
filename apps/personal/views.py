from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Empleado, Contrato, Bitacora
from .forms import EmpleadoForm, ContratoForm


@login_required
def empleados_lista(request):
    q = request.GET.get('q', '').strip()
    qs = Empleado.objects.select_related('persona').all()
    if q:
        qs = qs.filter(
            Q(persona__nombre__icontains=q) |
            Q(persona__ci__icontains=q)
        )
    page = Paginator(qs, 15).get_page(request.GET.get('page'))
    return render(request, 'personal/empleados_lista.html', {'empleados': page, 'q': q})


@login_required
def empleado_crear(request):
    form = EmpleadoForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Empleado registrado.')
        return redirect('personal:empleados')
    return render(request, 'personal/empleado_form.html', {'form': form, 'titulo': 'Nuevo Empleado'})


@login_required
def empleado_editar(request, pk):
    obj = get_object_or_404(Empleado, pk=pk)
    form = EmpleadoForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        messages.success(request, 'Empleado actualizado.')
        return redirect('personal:empleados')
    return render(request, 'personal/empleado_form.html', {'form': form, 'titulo': 'Editar Empleado'})


@login_required
def contratos_lista(request):
    qs = Contrato.objects.select_related('empleado__persona', 'turno').all()
    page = Paginator(qs, 15).get_page(request.GET.get('page'))
    return render(request, 'personal/contratos_lista.html', {'contratos': page})


@login_required
def contrato_crear(request):
    form = ContratoForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Contrato registrado.')
        return redirect('personal:contratos')
    return render(request, 'personal/contrato_form.html', {'form': form, 'titulo': 'Nuevo Contrato'})


@login_required
def bitacora(request):
    qs = Bitacora.objects.select_related('login__empleado__persona').order_by('-fecha')
    page = Paginator(qs, 30).get_page(request.GET.get('page'))
    return render(request, 'personal/bitacora.html', {'bitacora': page})
