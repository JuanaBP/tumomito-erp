from django.contrib import admin
from .models import Proveedor


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ['empresa', 'nit', 'representante_legal', 'pais', 'telefono', 'activo']
    search_fields = ['empresa', 'nit', 'representante_legal']
    list_filter = ['pais', 'activo']
