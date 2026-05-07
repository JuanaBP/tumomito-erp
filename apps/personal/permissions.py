"""
Sistema de permisos basado en roles.

Uso en vistas:
    from apps.personal.permissions import requires_module

    @requires_module('ventas')
    def lista_ventas(request):
        ...

Uso en templates (cargar tag al inicio del template):
    {% load permisos %}
    {% if request|tiene_acceso:'ventas' %}
        <a href="...">Ver ventas</a>
    {% endif %}
"""
from functools import wraps
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseForbidden


def get_empleado(user):
    """Devuelve el Empleado asociado al User, o None."""
    if not user.is_authenticated:
        return None
    return getattr(user, 'empleado_perfil', None)


def tiene_acceso(user, modulo_codigo):
    """Devuelve True si el user tiene acceso al modulo."""
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    empleado = get_empleado(user)
    if not empleado:
        return False
    return empleado.tiene_acceso(modulo_codigo)


def modulos_del_usuario(user):
    """Lista de codigos de modulos a los que el user tiene acceso."""
    if not user.is_authenticated:
        return []
    if user.is_superuser:
        return ['__all__']  # marca especial
    empleado = get_empleado(user)
    if not empleado or not empleado.rol or not empleado.activo:
        return []
    if empleado.rol.es_admin:
        return ['__all__']
    return list(empleado.rol.modulos or [])


def requires_module(modulo_codigo):
    """Decorador que verifica que el usuario tenga acceso al modulo."""
    def decorator(view_func):
        @wraps(view_func)
        @login_required(login_url='login')
        def wrapper(request, *args, **kwargs):
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            empleado = get_empleado(request.user)
            if not empleado:
                messages.error(request, 'Tu usuario no tiene un perfil de empleado asignado.')
                return redirect('login')
            if not empleado.activo:
                messages.error(request, 'Tu cuenta de empleado esta desactivada.')
                return redirect('login')
            if not empleado.tiene_acceso(modulo_codigo):
                messages.error(request,
                    f'No tienes permisos para acceder a este modulo. Contacta al administrador.')
                return redirect('dashboard:home')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def requires_admin(view_func):
    """Decorador que requiere que el usuario sea superuser O tenga rol con es_admin=True."""
    @wraps(view_func)
    @login_required(login_url='login')
    def wrapper(request, *args, **kwargs):
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        empleado = get_empleado(request.user)
        if not empleado or not empleado.rol or not empleado.rol.es_admin:
            messages.error(request, 'Solo administradores pueden acceder a esta seccion.')
            return redirect('dashboard:home')
        return view_func(request, *args, **kwargs)
    return wrapper
