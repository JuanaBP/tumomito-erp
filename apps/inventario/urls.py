from django.urls import path
from . import views

app_name = 'inventario'

urlpatterns = [
    # Productos
    path('productos/', views.productos_lista, name='productos'),
    path('productos/nuevo/', views.producto_crear, name='producto_crear'),
    path('productos/<int:pk>/', views.producto_detalle, name='producto_detalle'),
    path('productos/<int:pk>/editar/', views.producto_editar, name='producto_editar'),
    path('productos/<int:pk>/eliminar/', views.producto_eliminar, name='producto_eliminar'),

    # Inventario / Lotes
    path('lotes/', views.inventario_lista, name='lotes'),
    path('lotes/nuevo/', views.inventario_crear, name='lote_crear'),
    path('lotes/<int:pk>/editar/', views.inventario_editar, name='lote_editar'),
]
