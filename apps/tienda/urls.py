from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'tienda'

urlpatterns = [
    # Publico
    path('', views.home, name='home'),
    path('catalogo/', views.catalogo, name='catalogo'),
    path('producto/<slug:slug>/', views.detalle_producto, name='producto'),

    # Carrito
    path('carrito/', views.carrito_ver, name='carrito'),
    path('carrito/agregar/<int:producto_id>/', views.carrito_agregar, name='carrito_agregar'),
    path('carrito/eliminar/<int:producto_id>/', views.carrito_eliminar, name='carrito_eliminar'),
    path('carrito/vaciar/', views.carrito_vaciar, name='carrito_vaciar'),

    # Cuenta del cliente
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_cliente, name='login'),
    path('logout/', LogoutView.as_view(next_page='tienda:home'), name='logout'),

    # Checkout y pedidos
    path('checkout/', views.checkout, name='checkout'),
    path('direccion/nueva/', views.direccion_nueva, name='direccion_nueva'),
    path('pedido/<int:pk>/pago/', views.pedido_pago, name='pedido_pago'),
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),
    path('mis-pedidos/<int:pk>/', views.mi_pedido_detalle, name='mi_pedido_detalle'),

    # Admin (desde el ERP)
    path('admin/pedidos/', views.admin_pedidos, name='admin_pedidos'),
    path('admin/pedidos/<int:pk>/', views.admin_pedido_detalle, name='admin_pedido_detalle'),
    path('admin/pedidos/<int:pk>/confirmar/', views.admin_pedido_confirmar, name='admin_pedido_confirmar'),
    path('admin/pedidos/<int:pk>/estado/', views.admin_pedido_estado, name='admin_pedido_estado'),
]
