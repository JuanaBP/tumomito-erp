from django.urls import path
from . import views

app_name = 'personal'

urlpatterns = [
    path('empleados/', views.empleados_lista, name='empleados'),
    path('empleados/nuevo/', views.empleado_crear, name='empleado_crear'),
    path('empleados/<int:pk>/editar/', views.empleado_editar, name='empleado_editar'),

    path('contratos/', views.contratos_lista, name='contratos'),
    path('contratos/nuevo/', views.contrato_crear, name='contrato_crear'),

    path('bitacora/', views.bitacora, name='bitacora'),
]
