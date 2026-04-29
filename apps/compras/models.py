from django.db import models
from apps.proveedores.models import Proveedor
from apps.personal.models import Empleado
from apps.inventario.models import Producto


class NotaCompra(models.Model):
    MONEDA_CHOICES = [
        ('BOB', 'Boliviano'),
        ('USD', 'Dolar Americano'),
        ('EUR', 'Euro'),
        ('CNY', 'Yuan'),
    ]
    fecha = models.DateField()
    hora = models.TimeField()
    monto_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    moneda = models.CharField(max_length=10, choices=MONEDA_CHOICES, default='BOB')
    tipo_cambio = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT)
    empleado = models.ForeignKey(Empleado, on_delete=models.PROTECT)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Nota de Compra"
        verbose_name_plural = "Notas de Compra"
        db_table = "nota_compra"
        ordering = ['-fecha', '-hora']

    def __str__(self):
        return f"NC-{self.id:06d} - {self.proveedor.empresa}"

    def calcular_total(self):
        total = sum(d.subtotal for d in self.detalles.all())
        self.monto_total = total
        self.save(update_fields=['monto_total'])
        return total


class DetalleCompra(models.Model):
    concepto = models.CharField(max_length=50, blank=True)
    cantidad = models.PositiveIntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    nota_compra = models.ForeignKey(NotaCompra, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)

    class Meta:
        verbose_name = "Detalle de Compra"
        verbose_name_plural = "Detalles de Compra"
        db_table = "detalle_compra"

    def __str__(self):
        return f"{self.producto.nombre} x{self.cantidad}"

    @property
    def subtotal(self):
        return self.cantidad * self.precio
