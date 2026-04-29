from django.db import models
from apps.clientes.models import Cliente
from apps.personal.models import Empleado
from apps.inventario.models import Inventario, Producto


class NotaVenta(models.Model):
    MONEDA_CHOICES = [
        ('BOB', 'Boliviano'),
        ('USD', 'Dolar Americano'),
    ]
    fecha = models.DateField()
    hora = models.TimeField()
    monto_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    moneda = models.CharField(max_length=10, choices=MONEDA_CHOICES, default='BOB')
    tipo_cambio = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    empleado = models.ForeignKey(Empleado, on_delete=models.PROTECT)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Nota de Venta"
        verbose_name_plural = "Notas de Venta"
        db_table = "nota_venta"
        ordering = ['-fecha', '-hora']

    def __str__(self):
        return f"NV-{self.id:06d} - {self.cliente.persona.nombre}"

    def calcular_total(self):
        total = sum(d.subtotal for d in self.detalles.all())
        self.monto_total = total
        self.save(update_fields=['monto_total'])
        return total


class DetalleVenta(models.Model):
    concepto = models.CharField(max_length=50, blank=True)
    cantidad = models.PositiveIntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    nota_venta = models.ForeignKey(NotaVenta, on_delete=models.CASCADE, related_name='detalles')
    inventario = models.ForeignKey(Inventario, on_delete=models.PROTECT, related_name='ventas')

    class Meta:
        verbose_name = "Detalle de Venta"
        verbose_name_plural = "Detalles de Venta"
        db_table = "detalle_venta"

    def __str__(self):
        return f"{self.inventario.producto.nombre} x{self.cantidad}"

    @property
    def subtotal(self):
        return self.cantidad * self.precio

    @property
    def producto(self):
        return self.inventario.producto

    def save(self, *args, **kwargs):
        # Descontar de inventario si es nuevo
        if self.pk is None:
            if self.inventario.cantidad_disponible >= self.cantidad:
                self.inventario.cantidad_disponible -= self.cantidad
                self.inventario.save()
            else:
                raise ValueError(f"Stock insuficiente. Disponible: {self.inventario.cantidad_disponible}")
        super().save(*args, **kwargs)
