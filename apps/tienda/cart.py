"""Carrito de compras almacenado en la sesion del usuario."""
from decimal import Decimal
from apps.inventario.models import Producto

CARRITO_KEY = 'carrito'


class Carrito:
    def __init__(self, request):
        self.session = request.session
        self.request = request
        carrito = self.session.get(CARRITO_KEY)
        if not carrito:
            carrito = self.session[CARRITO_KEY] = {}
        self.carrito = carrito
        # Cliente para calcular precio mayorista/minorista
        self.cliente = None
        if request.user.is_authenticated:
            self.cliente = getattr(request.user, 'cliente_perfil', None)

    def agregar(self, producto, cantidad=1, sumar=True):
        pid = str(producto.id)
        nueva = cantidad
        if pid in self.carrito and sumar:
            nueva = self.carrito[pid]['cantidad'] + cantidad

        # Verificar stock
        if nueva > producto.stock_total:
            nueva = producto.stock_total
        if nueva <= 0:
            self.eliminar(producto)
            return

        self.carrito[pid] = {
            'cantidad': nueva,
            'producto_id': producto.id,
        }
        self.guardar()

    def eliminar(self, producto):
        pid = str(producto.id)
        if pid in self.carrito:
            del self.carrito[pid]
            self.guardar()

    def vaciar(self):
        self.session[CARRITO_KEY] = {}
        self.guardar()

    def guardar(self):
        self.session.modified = True

    def items(self):
        """Devuelve lista de items con producto, cantidad, precio aplicable y subtotal."""
        ids = [int(pid) for pid in self.carrito.keys()]
        productos = {p.id: p for p in Producto.objects.filter(id__in=ids)}
        resultado = []
        for pid_str, data in self.carrito.items():
            pid = int(pid_str)
            producto = productos.get(pid)
            if not producto:
                continue
            cantidad = data['cantidad']
            precio = producto.precio_para_cliente(self.cliente, cantidad)
            es_mayorista = (
                self.cliente and self.cliente.es_mayorista
                and producto.precio_mayorista > 0
                and cantidad >= producto.cant_min_mayorista
            )
            resultado.append({
                'producto': producto,
                'cantidad': cantidad,
                'precio_unitario': precio,
                'subtotal': precio * cantidad,
                'es_mayorista': bool(es_mayorista),
                'stock_disponible': producto.stock_total,
            })
        return resultado

    @property
    def total_items(self):
        return sum(it['cantidad'] for it in self.carrito.values())

    @property
    def total(self):
        return sum(it['subtotal'] for it in self.items())

    def __len__(self):
        return self.total_items

    def __iter__(self):
        return iter(self.items())
