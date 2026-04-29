from django.contrib import admin
from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['persona', 'nit', 'razon_social']
    search_fields = ['persona__nombre', 'persona__ci', 'nit']
