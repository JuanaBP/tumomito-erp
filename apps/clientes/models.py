from django.db import models
from django.contrib.auth.models import User
from apps.core.models import Persona


class Cliente(models.Model):
    TIPO_CHOICES = [
        ('minorista', 'Minorista'),
        ('mayorista', 'Mayorista'),
    ]

    persona = models.OneToOneField(
        Persona,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='cliente'
    )
    nit = models.CharField(max_length=20, verbose_name="NIT")
    razon_social = models.CharField(max_length=60, blank=True, null=True, verbose_name="Razon Social")
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='minorista')
    user = models.OneToOneField(
        User, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='cliente_perfil',
        help_text='Usuario para acceder a la tienda online'
    )
    creado = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        db_table = "cliente"

    def __str__(self):
        return f"{self.persona.nombre} ({self.nit})"

    @property
    def nombre(self):
        return self.persona.nombre

    @property
    def ci(self):
        return self.persona.ci

    @property
    def email(self):
        return self.persona.email

    @property
    def celular(self):
        return self.persona.celular

    @property
    def es_mayorista(self):
        return self.tipo == 'mayorista'
