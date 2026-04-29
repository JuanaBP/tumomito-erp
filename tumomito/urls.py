"""
URL Configuration TUMOMITO ERP
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Autenticacion
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Modulos
    path('', include('apps.dashboard.urls', namespace='dashboard')),
    path('clientes/', include('apps.clientes.urls', namespace='clientes')),
    path('proveedores/', include('apps.proveedores.urls', namespace='proveedores')),
    path('inventario/', include('apps.inventario.urls', namespace='inventario')),
    path('compras/', include('apps.compras.urls', namespace='compras')),
    path('ventas/', include('apps.ventas.urls', namespace='ventas')),
    path('personal/', include('apps.personal.urls', namespace='personal')),
    path('tienda/', include('apps.tienda.urls', namespace='tienda')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
