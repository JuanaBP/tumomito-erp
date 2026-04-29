from django.db import models
from django.contrib.auth.models import User
from apps.core.models import Persona, Estado, Turno


class Empleado(models.Model):
    ESTADO_CIVIL_CHOICES = [
        ('Soltero', 'Soltero/a'),
        ('Casado', 'Casado/a'),
        ('Divorciado', 'Divorciado/a'),
        ('Viudo', 'Viudo/a'),
    ]
    persona = models.OneToOneField(
        Persona,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='empleado'
    )
    telf_contacto = models.CharField(max_length=20, verbose_name="Telefono de contacto")
    nombre_contacto = models.CharField(max_length=60, verbose_name="Nombre de contacto")
    estado_civil = models.CharField(max_length=20, choices=ESTADO_CIVIL_CHOICES)

    class Meta:
        verbose_name = "Empleado"
        verbose_name_plural = "Empleados"
        db_table = "empleado"

    def __str__(self):
        return self.persona.nombre


class Contrato(models.Model):
    TIPO_CHOICES = [
        ('Indefinido', 'Indefinido'),
        ('Plazo Fijo', 'Plazo Fijo'),
        ('Por Obra', 'Por Obra'),
        ('Practicas', 'Practicas'),
    ]
    cargo_laboral = models.CharField(max_length=50)
    tipo = models.CharField(max_length=40, choices=TIPO_CHOICES)
    salario = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(blank=True, null=True)
    turno = models.ForeignKey(Turno, on_delete=models.PROTECT)
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='contratos')

    class Meta:
        verbose_name = "Contrato"
        verbose_name_plural = "Contratos"
        db_table = "contrato"
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f"{self.empleado} - {self.cargo_laboral}"


class Login(models.Model):
    nombre_log = models.CharField(max_length=20, verbose_name="Nombre de usuario")
    passwordlog = models.CharField(max_length=255)
    email_rec = models.EmailField(verbose_name="Email de recuperacion")
    fechalog = models.DateTimeField(auto_now_add=True)
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    estado = models.ForeignKey(Estado, on_delete=models.PROTECT)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = "Login"
        verbose_name_plural = "Logins"
        db_table = "login"

    def __str__(self):
        return self.nombre_log


class Bitacora(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    login = models.ForeignKey(Login, on_delete=models.CASCADE, related_name='bitacoras')
    accion = models.CharField(max_length=200, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        verbose_name = "Bitacora"
        verbose_name_plural = "Bitacoras"
        db_table = "bitacora"
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.login} - {self.fecha}"
