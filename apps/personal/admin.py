from django.contrib import admin
from .models import Empleado, Contrato, Login, Bitacora


@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ['persona', 'estado_civil', 'telf_contacto']
    search_fields = ['persona__nombre', 'persona__ci']


@admin.register(Contrato)
class ContratoAdmin(admin.ModelAdmin):
    list_display = ['empleado', 'cargo_laboral', 'tipo', 'salario', 'fecha_inicio', 'fecha_fin']
    list_filter = ['tipo']


@admin.register(Login)
class LoginAdmin(admin.ModelAdmin):
    list_display = ['nombre_log', 'empleado', 'estado', 'fechalog']
    search_fields = ['nombre_log']


@admin.register(Bitacora)
class BitacoraAdmin(admin.ModelAdmin):
    list_display = ['fecha', 'login', 'accion', 'ip']
    list_filter = ['fecha']
    readonly_fields = ['fecha', 'login', 'accion', 'ip']
