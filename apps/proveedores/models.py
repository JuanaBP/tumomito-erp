from django.db import models


class Proveedor(models.Model):
    PAIS_CHOICES = [
        ('Bolivia', 'Bolivia'),
        ('China', 'China'),
        ('Brasil', 'Brasil'),
        ('Argentina', 'Argentina'),
        ('Estados Unidos', 'Estados Unidos'),
        ('Espana', 'Espana'),
        ('Mexico', 'Mexico'),
        ('Otro', 'Otro'),
    ]
    empresa = models.CharField(max_length=100)
    nit = models.CharField(max_length=20, unique=True, verbose_name="NIT")
    representante_legal = models.CharField(max_length=100)
    pais = models.CharField(max_length=50, choices=PAIS_CHOICES, default='Bolivia')
    direccion = models.TextField(blank=True, null=True)
    telefono = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        db_table = "proveedor"
        ordering = ['empresa']

    def __str__(self):
        return f"{self.empresa} ({self.nit})"
