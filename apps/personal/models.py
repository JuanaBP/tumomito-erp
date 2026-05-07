from django.db import models
from django.contrib.auth.models import User
from apps.core.models import Persona, Estado, Turno


# Codigos de modulo del sistema (usados para permisos)
MODULOS_SISTEMA = [
    ('dashboard', 'Dashboard'),
    ('pos', 'Punto de Venta'),
    ('ventas', 'Notas de Venta'),
    ('clientes', 'Clientes'),
    ('compras', 'Compras'),
    ('proveedores', 'Proveedores'),
    ('productos', 'Productos'),
    ('categorias', 'Categorias'),
    ('inventario', 'Inventario / Stock'),
    ('empleados', 'Empleados'),
    ('roles', 'Roles y Permisos'),
    ('tienda_admin', 'Pedidos Online (Admin)'),
    ('bitacora', 'Bitacora'),
    ('reportes', 'Reportes'),
]


class Rol(models.Model):
    """Rol con un conjunto de modulos a los que da acceso."""
    nombre = models.CharField(max_length=50, unique=True)
    codigo = models.SlugField(max_length=30, unique=True,
                              help_text='Identificador unico (ej: vendedor, cajero)')
    descripcion = models.TextField(blank=True)
    modulos = models.JSONField(default=list,
                               help_text='Lista de codigos de modulos accesibles')
    es_admin = models.BooleanField(default=False,
                                   help_text='Si es True, tiene acceso a todo')
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Rol"
        verbose_name_plural = "Roles"
        db_table = "rol"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    def tiene_modulo(self, codigo):
        if self.es_admin:
            return True
        return codigo in (self.modulos or [])

    @property
    def cantidad_modulos(self):
        if self.es_admin:
            return 'Todos'
        return len(self.modulos or [])


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
    estado_civil = models.CharField(max_length=20, choices=ESTADO_CIVIL_CHOICES, default='Soltero')

    # Nuevos campos para roles y auth
    rol = models.ForeignKey(Rol, on_delete=models.PROTECT, null=True, blank=True,
                            related_name='empleados')
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='empleado_perfil',
                                help_text='Usuario para acceder al sistema')
    activo = models.BooleanField(default=True)
    fecha_ingreso = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "Empleado"
        verbose_name_plural = "Empleados"
        db_table = "empleado"

    def __str__(self):
        return self.persona.nombre

    @property
    def nombre(self):
        return self.persona.nombre

    @property
    def email(self):
        return self.persona.email

    def tiene_acceso(self, modulo_codigo):
        if self.user and self.user.is_superuser:
            return True
        if not self.rol or not self.activo:
            return False
        return self.rol.tiene_modulo(modulo_codigo)


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
    login = models.ForeignKey(Login, on_delete=models.CASCADE, related_name='bitacoras', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='bitacoras', null=True, blank=True)
    accion = models.CharField(max_length=200, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        verbose_name = "Bitacora"
        verbose_name_plural = "Bitacoras"
        db_table = "bitacora"
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.user} - {self.fecha}" if self.user else f"Anonimo - {self.fecha}"
