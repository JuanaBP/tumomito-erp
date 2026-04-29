from django.db import models
from django.db.models import Sum
from django.utils.text import slugify


class Producto(models.Model):
    CATEGORIA_CHOICES = [
        ('Hogar', 'Hogar'),
        ('Tecnologia', 'Tecnologia'),
        ('Juguetes', 'Juguetes'),
        ('Ropa', 'Ropa'),
        ('Belleza', 'Belleza'),
        ('Papeleria', 'Papeleria'),
        ('Ferreteria', 'Ferreteria'),
        ('Alimentos', 'Alimentos'),
        ('Bebidas', 'Bebidas'),
        ('Otros', 'Otros'),
    ]
    codigo = models.CharField(max_length=30, unique=True, verbose_name="Codigo SKU")
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    nombre = models.CharField(max_length=100)
    categoria = models.CharField(max_length=50, choices=CATEGORIA_CHOICES)
    subcategoria = models.CharField(max_length=50, blank=True, null=True)
    fabricante = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True, null=True)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                       help_text='Precio minorista (publico)')
    precio_mayorista = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                           help_text='Precio para mayoristas (0 = mismo que minorista)')
    cant_min_mayorista = models.PositiveIntegerField(default=12,
                                                     help_text='Cantidad minima para precio mayorista')
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    destacado = models.BooleanField(default=False, help_text='Aparece en la home de la tienda')
    visible_tienda = models.BooleanField(default=True, help_text='Mostrar en tienda online')
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        db_table = "producto"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(f'{self.codigo}-{self.nombre}')[:115]
            self.slug = base
        super().save(*args, **kwargs)

    @property
    def stock_total(self):
        result = self.lotes.aggregate(total=Sum('cantidad_disponible'))
        return result['total'] or 0

    @property
    def stock_bajo(self):
        return self.stock_total < 10

    def precio_para_cliente(self, cliente, cantidad=1):
        """Devuelve el precio aplicable segun tipo de cliente y cantidad."""
        if (cliente and cliente.es_mayorista
                and self.precio_mayorista > 0
                and cantidad >= self.cant_min_mayorista):
            return self.precio_mayorista
        return self.precio_venta

    def tiene_descuento_mayorista(self):
        return self.precio_mayorista > 0 and self.precio_mayorista < self.precio_venta


class Inventario(models.Model):
    """Lote de inventario para un producto especifico."""
    nro_lote = models.CharField(max_length=50, verbose_name="Nro de Lote")
    cantidad_recibida = models.PositiveIntegerField()
    cantidad_disponible = models.PositiveIntegerField()
    fecha_adquision = models.DateField(verbose_name="Fecha de adquisicion")
    fecha_emision = models.DateField(blank=True, null=True)
    fecha_vencimiento = models.DateField(blank=True, null=True)
    coste_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    coste_final = models.DecimalField(max_digits=10, decimal_places=2)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name='lotes')
    detalle_compra = models.ForeignKey(
        'compras.DetalleCompra',
        on_delete=models.PROTECT,
        related_name='lotes',
        null=True, blank=True
    )

    class Meta:
        verbose_name = "Inventario (Lote)"
        verbose_name_plural = "Inventario (Lotes)"
        db_table = "inventario"
        ordering = ['fecha_adquision']  # FIFO

    def __str__(self):
        return f"Lote {self.nro_lote} - {self.producto.nombre}"
