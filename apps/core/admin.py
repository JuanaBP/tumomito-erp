from django.contrib import admin
from .models import Persona, Estado, Turno


@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'ci', 'celular', 'email', 'nacionalidad']
    search_fields = ['nombre', 'ci', 'email']
    list_filter = ['nacionalidad']


@admin.register(Estado)
class EstadoAdmin(admin.ModelAdmin):
    list_display = ['id', 'descripcion']


@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = ['id', 'tipo', 'jornada']
    list_filter = ['tipo', 'jornada']
