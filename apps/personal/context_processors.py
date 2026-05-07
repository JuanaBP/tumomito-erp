from apps.personal.permissions import get_empleado, modulos_del_usuario


def usuario_perfil(request):
    """Expone el empleado y modulos disponibles en todos los templates."""
    if not request.user.is_authenticated:
        return {'empleado_actual': None, 'modulos_disponibles': []}
    return {
        'empleado_actual': get_empleado(request.user),
        'modulos_disponibles': modulos_del_usuario(request.user),
    }
