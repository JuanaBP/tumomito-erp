from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from django.core.paginator import Paginator

from apps.personal.permissions import requires_module
from .models import Empleado, Contrato, Bitacora, Rol, MODULOS_SISTEMA
from .forms import EmpleadoForm, ContratoForm, RolForm


# ==========================================================
# ROLES - CRUD (solo admin)
# ==========================================================
@requires_module('roles')
def roles_lista(request):
    qs = Rol.objects.all().order_by('-es_admin', 'nombre')
    return render(request, 'personal/roles_lista.html', {
        'roles': qs,
        'modulos_sistema': dict(MODULOS_SISTEMA),
    })


@requires_module('roles')
def rol_crear(request):
    form = RolForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Rol creado.')
        return redirect('personal:roles')
    return render(request, 'personal/rol_form.html', {
        'form': form, 'titulo': 'Nuevo Rol',
        'modulos_sistema': MODULOS_SISTEMA,
    })


@requires_module('roles')
def rol_editar(request, pk):
    obj = get_object_or_404(Rol, pk=pk)
    form = RolForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        messages.success(request, 'Rol actualizado.')
        return redirect('personal:roles')
    return render(request, 'personal/rol_form.html', {
        'form': form, 'titulo': f'Editar Rol: {obj.nombre}',
        'rol': obj, 'modulos_sistema': MODULOS_SISTEMA,
    })


@requires_module('roles')
def rol_eliminar(request, pk):
    obj = get_object_or_404(Rol, pk=pk)
    if obj.empleados.count() > 0:
        messages.error(request,
            f'No se puede eliminar: {obj.empleados.count()} empleado(s) tienen este rol asignado.')
        return redirect('personal:roles')
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Rol eliminado.')
        return redirect('personal:roles')
    return render(request, 'personal/rol_eliminar.html', {'rol': obj})


# ==========================================================
# EMPLEADOS - CRUD (solo admin)
# ==========================================================
@requires_module('empleados')
def empleados_lista(request):
    q = request.GET.get('q', '').strip()
    rol_id = request.GET.get('rol', '').strip()
    qs = Empleado.objects.select_related('persona', 'rol', 'user').all()
    if q:
        qs = qs.filter(
            Q(persona__nombre__icontains=q) |
            Q(persona__ci__icontains=q) |
            Q(user__username__icontains=q)
        )
    if rol_id:
        qs = qs.filter(rol_id=rol_id)
    page = Paginator(qs, 15).get_page(request.GET.get('page'))
    return render(request, 'personal/empleados_lista.html', {
        'empleados': page,
        'q': q,
        'rol_id': rol_id,
        'roles': Rol.objects.filter(activo=True),
    })


@requires_module('empleados')
def empleado_crear(request):
    form = EmpleadoForm(request.POST or None)
    if form.is_valid():
        emp = form.save()
        messages.success(request,
            f'Empleado "{emp.nombre}" creado con rol {emp.rol.nombre}. '
            f'Acceso: usuario "{emp.user.username}".')
        return redirect('personal:empleados')
    return render(request, 'personal/empleado_form.html', {
        'form': form, 'titulo': 'Nuevo Empleado',
    })


@requires_module('empleados')
def empleado_editar(request, pk):
    emp = get_object_or_404(Empleado, pk=pk)
    form = EmpleadoForm(request.POST or None, instance=emp)
    if form.is_valid():
        form.save()
        messages.success(request, 'Empleado actualizado.')
        return redirect('personal:empleados')
    return render(request, 'personal/empleado_form.html', {
        'form': form, 'titulo': f'Editar: {emp.nombre}',
        'empleado': emp,
    })


@requires_module('empleados')
def empleado_resetear(request, pk):
    """Resetea la contrasena del empleado y la muestra una sola vez."""
    emp = get_object_or_404(Empleado, pk=pk)
    if not emp.user:
        messages.error(request, 'Este empleado no tiene usuario asignado.')
        return redirect('personal:empleados')
    if request.method == 'POST':
        import secrets, string
        nueva = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(10))
        emp.user.set_password(nueva)
        emp.user.save()
        messages.success(request,
            f'Contrasena reseteada para "{emp.user.username}". Nueva contrasena: {nueva} '
            f'(copialaa AHORA, no la veras de nuevo)')
        return redirect('personal:empleados')
    return render(request, 'personal/empleado_resetear.html', {'empleado': emp})


# ==========================================================
# CONTRATOS
# ==========================================================
@requires_module('empleados')
def contratos_lista(request):
    qs = Contrato.objects.select_related('empleado__persona', 'turno').all()
    page = Paginator(qs, 15).get_page(request.GET.get('page'))
    return render(request, 'personal/contratos_lista.html', {'contratos': page})


@requires_module('empleados')
def contrato_crear(request):
    form = ContratoForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Contrato registrado.')
        return redirect('personal:contratos')
    return render(request, 'personal/contrato_form.html', {'form': form, 'titulo': 'Nuevo Contrato'})


# ==========================================================
# BITACORA
# ==========================================================
@requires_module('bitacora')
def bitacora(request):
    qs = Bitacora.objects.select_related('user').order_by('-fecha')
    page = Paginator(qs, 30).get_page(request.GET.get('page'))
    return render(request, 'personal/bitacora.html', {'bitacora': page})
