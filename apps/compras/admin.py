from django.contrib import admin
from .models import NotaCompra, DetalleCompra


class DetalleCompraInline(admin.TabularInline):
    model = DetalleCompra
    extra = 0


@admin.register(NotaCompra)
class NotaCompraAdmin(admin.ModelAdmin):
    list_display = ['id', 'fecha', 'proveedor', 'empleado', 'monto_total', 'moneda']
    list_filter = ['fecha', 'moneda', 'proveedor']
    inlines = [DetalleCompraInline]
