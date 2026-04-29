from django.contrib import admin
from .models import NotaVenta, DetalleVenta


class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 0


@admin.register(NotaVenta)
class NotaVentaAdmin(admin.ModelAdmin):
    list_display = ['id', 'fecha', 'cliente', 'empleado', 'monto_total', 'moneda']
    list_filter = ['fecha', 'moneda']
    search_fields = ['cliente__persona__nombre']
    inlines = [DetalleVentaInline]
