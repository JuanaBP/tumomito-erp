from django.urls import path
from . import views

app_name = 'compras'

urlpatterns = [
    path('', views.lista, name='lista'),
    path('nueva/', views.nueva, name='nueva'),
    path('confirmar/', views.confirmar, name='confirmar'),
    path('<int:pk>/', views.detalle, name='detalle'),
]
