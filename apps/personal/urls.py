from django.urls import path
from . import views

app_name = 'personal'

urlpatterns = [
    # Empleados
    path('empleados/', views.empleados_lista, name='empleados'),
    path('empleados/nuevo/', views.empleado_crear, name='empleado_crear'),
    path('empleados/<int:pk>/editar/', views.empleado_editar, name='empleado_editar'),
    path('empleados/<int:pk>/resetear/', views.empleado_resetear, name='empleado_resetear'),

    # Roles
    path('roles/', views.roles_lista, name='roles'),
    path('roles/nuevo/', views.rol_crear, name='rol_crear'),
    path('roles/<int:pk>/editar/', views.rol_editar, name='rol_editar'),
    path('roles/<int:pk>/eliminar/', views.rol_eliminar, name='rol_eliminar'),

    # Contratos
    path('contratos/', views.contratos_lista, name='contratos'),
    path('contratos/nuevo/', views.contrato_crear, name='contrato_crear'),

    # Bitacora
    path('bitacora/', views.bitacora, name='bitacora'),
]
