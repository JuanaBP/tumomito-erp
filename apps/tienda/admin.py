from django.contrib import admin
from .models import Pedido, DetallePedido, Direccion


class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 0
    readonly_fields = ['producto', 'cantidad', 'precio_unitario', 'es_mayorista']


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ['numero', 'cliente', 'fecha_pedido', 'estado', 'metodo_pago', 'monto_total']
    list_filter = ['estado', 'metodo_pago', 'fecha_pedido']
    search_fields = ['numero', 'cliente__persona__nombre']
    inlines = [DetallePedidoInline]
    readonly_fields = ['numero', 'fecha_pedido', 'monto_subtotal', 'monto_total', 'nota_venta']


@admin.register(Direccion)
class DireccionAdmin(admin.ModelAdmin):
    list_display = ['cliente', 'alias', 'ciudad', 'zona', 'es_principal']
    list_filter = ['ciudad']
    search_fields = ['cliente__persona__nombre', 'zona']
