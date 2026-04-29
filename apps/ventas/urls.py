from django.urls import path
from . import views

app_name = 'ventas'

urlpatterns = [
    path('', views.lista, name='lista'),
    path('pos/', views.pos, name='pos'),
    path('pos/api/productos/', views.api_productos_disponibles, name='api_productos'),
    path('pos/confirmar/', views.pos_confirmar, name='pos_confirmar'),
    path('<int:pk>/', views.detalle, name='detalle'),
]
