from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from apps.clientes.models import Cliente
from apps.inventario.models import Producto


class Direccion(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='direcciones')
    alias = models.CharField(max_length=50, help_text='Ej: Casa, Oficina')
    ciudad = models.CharField(max_length=50, default='Santa Cruz')
    zona = models.CharField(max_length=80)
    calle = models.CharField(max_length=120)
    numero = models.CharField(max_length=20, blank=True)
    referencia = models.TextField(blank=True, help_text='Referencias para encontrar el lugar')
    telefono = models.CharField(max_length=20)
    es_principal = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Direccion'
        verbose_name_plural = 'Direcciones'
        db_table = 'tienda_direccion'

    def __str__(self):
        return f"{self.alias} - {self.zona}"


class Pedido(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente de pago'),
        ('pagado', 'Pago reportado'),
        ('confirmado', 'Confirmado por TUMOMITO'),
        ('preparando', 'Preparando envio'),
        ('enviado', 'En camino'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]
    METODOS_PAGO = [
        ('transferencia', 'Transferencia bancaria'),
        ('qr', 'QR / Tigo Money'),
        ('contra_entrega', 'Pago contra entrega'),
    ]

    numero = models.CharField(max_length=20, unique=True, blank=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='pedidos')
    direccion = models.ForeignKey(Direccion, on_delete=models.PROTECT, null=True, blank=True)

    fecha_pedido = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')

    metodo_pago = models.CharField(max_length=20, choices=METODOS_PAGO)
    comprobante_pago = models.ImageField(upload_to='comprobantes/', blank=True, null=True)
    referencia_pago = models.CharField(max_length=100, blank=True)

    monto_subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    monto_envio = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    monto_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    observaciones = models.TextField(blank=True)
    nota_venta = models.OneToOneField(
        'ventas.NotaVenta', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='pedido_origen'
    )
    fecha_entrega = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Pedido Online'
        verbose_name_plural = 'Pedidos Online'
        db_table = 'tienda_pedido'
        ordering = ['-fecha_pedido']

    def __str__(self):
        return self.numero or f'Pedido #{self.id}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.numero:
            self.numero = f'PED-{self.fecha_pedido.year}-{self.id:06d}'
            super().save(update_fields=['numero'])

    def calcular_totales(self):
        sub = sum(d.subtotal for d in self.detalles.all())
        self.monto_subtotal = sub
        self.monto_total = sub + (self.monto_envio or Decimal('0'))
        self.save(update_fields=['monto_subtotal', 'monto_total'])

    @property
    def total_items(self):
        return sum(d.cantidad for d in self.detalles.all())

    @property
    def color_estado(self):
        return {
            'pendiente': 'warning',
            'pagado': 'info',
            'confirmado': 'primary',
            'preparando': 'primary',
            'enviado': 'success',
            'entregado': 'success',
            'cancelado': 'danger',
        }.get(self.estado, 'secondary')


class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    es_mayorista = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Detalle de Pedido'
        verbose_name_plural = 'Detalles de Pedido'
        db_table = 'tienda_detalle_pedido'

    def __str__(self):
        return f'{self.producto.nombre} x{self.cantidad}'

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario
