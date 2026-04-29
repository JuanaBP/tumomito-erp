from django.db import models


class Estado(models.Model):
    descripcion = models.CharField(max_length=20, verbose_name="Descripcion")

    class Meta:
        verbose_name = "Estado"
        verbose_name_plural = "Estados"
        db_table = "estado"

    def __str__(self):
        return self.descripcion


class Turno(models.Model):
    TIPO_CHOICES = [
        ('Diurno', 'Diurno'),
        ('Nocturno', 'Nocturno'),
        ('Mixto', 'Mixto'),
    ]
    JORNADA_CHOICES = [
        ('Tiempo Completo', 'Tiempo Completo'),
        ('Medio Tiempo', 'Medio Tiempo'),
        ('Por Horas', 'Por Horas'),
    ]
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    jornada = models.CharField(max_length=20, choices=JORNADA_CHOICES)

    class Meta:
        verbose_name = "Turno"
        verbose_name_plural = "Turnos"
        db_table = "turno"

    def __str__(self):
        return f"{self.tipo} - {self.jornada}"


class Persona(models.Model):
    NACIONALIDAD_CHOICES = [
        ('Boliviana', 'Boliviana'),
        ('Argentina', 'Argentina'),
        ('Brasilena', 'Brasilena'),
        ('Chilena', 'Chilena'),
        ('Peruana', 'Peruana'),
        ('Otra', 'Otra'),
    ]
    nombre = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()
    ci = models.CharField(max_length=20, unique=True, verbose_name="CI")
    nacionalidad = models.CharField(max_length=20, choices=NACIONALIDAD_CHOICES, default='Boliviana')
    direccion = models.TextField(blank=True, null=True)
    celular = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)

    class Meta:
        verbose_name = "Persona"
        verbose_name_plural = "Personas"
        db_table = "persona"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.ci})"
