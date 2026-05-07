from django import template
from apps.personal.permissions import tiene_acceso as _tiene_acceso

register = template.Library()


@register.filter(name='tiene_acceso')
def tiene_acceso_filter(user, modulo):
    """Uso: {% if user|tiene_acceso:'ventas' %}...{% endif %}"""
    return _tiene_acceso(user, modulo)


@register.simple_tag
def has_module(user, modulo):
    """Uso: {% has_module user 'ventas' as can %}{% if can %}...{% endif %}"""
    return _tiene_acceso(user, modulo)


@register.filter(name='get_item')
def get_item(d, key):
    """Uso: {{ mi_dict|get_item:'clave' }}"""
    if not d:
        return None
    if hasattr(d, 'get'):
        return d.get(key, key)
    return key
