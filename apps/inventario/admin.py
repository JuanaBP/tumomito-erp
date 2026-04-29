from django.contrib import admin
from .models import Producto, Inventario


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'categoria', 'fabricante', 'precio_venta', 'stock_total', 'activo']
    search_fields = ['codigo', 'nombre', 'fabricante']
    list_filter = ['categoria', 'activo']


@admin.register(Inventario)
class InventarioAdmin(admin.ModelAdmin):
    list_display = ['nro_lote', 'producto', 'cantidad_disponible', 'fecha_adquision', 'coste_unitario']
    search_fields = ['nro_lote', 'producto__nombre']
    list_filter = ['fecha_adquision']
