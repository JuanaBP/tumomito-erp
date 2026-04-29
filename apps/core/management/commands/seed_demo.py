"""
Comando: python manage.py seed_demo
Carga datos de prueba para TUMOMITO ERP.
"""
import random
from datetime import date, time, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction

from apps.core.models import Persona, Estado, Turno
from apps.personal.models import Empleado, Contrato, Login
from apps.clientes.models import Cliente
from apps.proveedores.models import Proveedor
from apps.inventario.models import Producto, Inventario
from apps.compras.models import NotaCompra, DetalleCompra
from apps.ventas.models import NotaVenta, DetalleVenta


class Command(BaseCommand):
    help = 'Carga datos demo para el ERP TUMOMITO'

    @transaction.atomic
    def handle(self, *args, **opts):
        self.stdout.write('Sembrando datos demo...')

        # Estados
        for d in ['Activo', 'Inactivo', 'Bloqueado']:
            Estado.objects.get_or_create(descripcion=d)

        # Turnos
        for t, j in [('Diurno', 'Tiempo Completo'), ('Diurno', 'Medio Tiempo'),
                     ('Nocturno', 'Tiempo Completo'), ('Mixto', 'Por Horas')]:
            Turno.objects.get_or_create(tipo=t, jornada=j)
        self.stdout.write('  Estados y turnos: OK')

        # Empleados
        empleados_data = [
            ('Juan Carlos Mendoza', '5847123', 'Boliviana', '70123456', 'juan@tumomito.bo'),
            ('Maria Laura Vega', '6398745', 'Boliviana', '71987654', 'maria@tumomito.bo'),
            ('Pedro Antonio Roca', '4521098', 'Boliviana', '72345678', 'pedro@tumomito.bo'),
        ]
        empleados = []
        for nombre, ci, nac, cel, email in empleados_data:
            persona, _ = Persona.objects.get_or_create(
                ci=ci,
                defaults={
                    'nombre': nombre, 'fecha_nacimiento': date(1990, 5, 15),
                    'nacionalidad': nac, 'celular': cel, 'email': email,
                    'direccion': 'Av. Cristo Redentor #123',
                }
            )
            emp, _ = Empleado.objects.get_or_create(
                persona=persona,
                defaults={'telf_contacto': '76543210', 'nombre_contacto': 'Familiar', 'estado_civil': 'Soltero'}
            )
            empleados.append(emp)
        self.stdout.write(f'  Empleados: {len(empleados)} OK')

        # Contratos
        turno = Turno.objects.first()
        for emp in empleados:
            Contrato.objects.get_or_create(
                empleado=emp,
                defaults={
                    'cargo_laboral': 'Vendedor', 'tipo': 'Indefinido',
                    'salario': Decimal('3500.00'), 'fecha_inicio': date(2024, 1, 1),
                    'turno': turno,
                }
            )

        # Vincular admin user al primer empleado para que actue como vendedor
        admin_user = User.objects.filter(is_superuser=True).first()
        if admin_user and empleados:
            estado_activo = Estado.objects.get(descripcion='Activo')
            Login.objects.get_or_create(
                user=admin_user,
                defaults={
                    'nombre_log': admin_user.username,
                    'passwordlog': '*',
                    'email_rec': admin_user.email or 'admin@tumomito.bo',
                    'empleado': empleados[0],
                    'estado': estado_activo,
                }
            )

        # Clientes
        clientes_data = [
            ('Ana Sofia Gutierrez', '9876543', '9876543012', 'Empresa Sol SRL'),
            ('Roberto Carlos Lima', '8765432', '8765432019', ''),
            ('Carla Patricia Mendez', '7654321', '7654321016', 'Distribuidora CPM'),
            ('Miguel Angel Suarez', '6543210', '6543210013', ''),
            ('Lucia Fernanda Rojas', '5432109', '5432109010', 'Tienda Lucia'),
        ]
        for nombre, ci, nit, razon in clientes_data:
            persona, _ = Persona.objects.get_or_create(
                ci=ci,
                defaults={
                    'nombre': nombre, 'fecha_nacimiento': date(1985, 8, 20),
                    'nacionalidad': 'Boliviana', 'celular': f'7{random.randint(1000000, 9999999)}',
                    'email': f"{nombre.split()[0].lower()}@email.com",
                }
            )
            Cliente.objects.get_or_create(persona=persona, defaults={'nit': nit, 'razon_social': razon})
        self.stdout.write(f'  Clientes: {len(clientes_data)} OK')

        # Proveedores
        proveedores_data = [
            ('Importadora ChinaTech S.A.', '1234567890', 'Wei Zhang', 'China'),
            ('Distribuidora Brasil Importa', '9876543210', 'Carlos Silva', 'Brasil'),
            ('Plasticorp SRL', '5544332211', 'Ana Maria Cordero', 'Bolivia'),
            ('Casa Idea Internacional', '3322114455', 'Luis Alberto Vega', 'Argentina'),
        ]
        proveedores = []
        for emp, nit, rep, pais in proveedores_data:
            p, _ = Proveedor.objects.get_or_create(
                nit=nit,
                defaults={'empresa': emp, 'representante_legal': rep, 'pais': pais,
                          'telefono': f'7{random.randint(1000000, 9999999)}',
                          'direccion': 'Zona industrial', 'email': 'contacto@proveedor.com'}
            )
            proveedores.append(p)
        self.stdout.write(f'  Proveedores: {len(proveedores)} OK')

        # Productos (variedad de categorias para una importadora)
        productos_data = [
            ('TEC-001', 'Audifonos Bluetooth Premium', 'Tecnologia', 'Inalambricos', 'SoundMax', 180, 65),
            ('TEC-002', 'Cargador USB-C 30W', 'Tecnologia', 'Cargadores', 'PowerTech', 75, 25),
            ('TEC-003', 'Mouse Inalambrico Ergonomico', 'Tecnologia', 'Perifericos', 'LogiTech', 120, 45),
            ('HOG-001', 'Set de ollas antiadherentes 5pz', 'Hogar', 'Cocina', 'CasaIdea', 450, 200),
            ('HOG-002', 'Organizador de armario plegable', 'Hogar', 'Almacenamiento', 'CasaIdea', 180, 80),
            ('JUG-001', 'Carrito control remoto 4x4', 'Juguetes', 'Vehiculos', 'SmartToys', 220, 95),
            ('JUG-002', 'Set de bloques de construccion 200pz', 'Juguetes', 'Educativos', 'Chikippon', 150, 60),
            ('ROP-001', 'Camisa formal blanca M', 'Ropa', 'Hombre', 'Acricolor', 110, 45),
            ('ROP-002', 'Vestido casual estampado L', 'Ropa', 'Mujer', 'Belia', 195, 80),
            ('BEL-001', 'Set de maquillaje profesional', 'Belleza', 'Maquillaje', 'Hinode', 280, 120),
            ('PAP-001', 'Agenda 2026 ejecutiva', 'Papeleria', 'Agendas', 'AgendasPro', 65, 22),
            ('FER-001', 'Caja herramientas 50 piezas', 'Ferreteria', 'Herramientas', 'Makro', 320, 145),
        ]
        productos = []
        for codigo, nombre, cat, subcat, fab, precio, costo in productos_data:
            p, created = Producto.objects.get_or_create(
                codigo=codigo,
                defaults={
                    'nombre': nombre, 'categoria': cat, 'subcategoria': subcat,
                    'fabricante': fab, 'precio_venta': Decimal(str(precio)),
                    'precio_mayorista': Decimal(str(round(precio * 0.80, 2))),  # 20% off mayoristas
                    'cant_min_mayorista': 12,
                    'descripcion': f'Producto importado {nombre}.',
                    'destacado': random.choice([True, False, False]),
                    'visible_tienda': True,
                }
            )
            productos.append((p, costo))
        self.stdout.write(f'  Productos: {len(productos)} OK')

        # Inventario (lotes)
        for p, costo in productos:
            for i in range(2):  # 2 lotes por producto
                cant = random.randint(15, 100)
                Inventario.objects.get_or_create(
                    nro_lote=f'L-{p.codigo}-00{i+1}',
                    defaults={
                        'cantidad_recibida': cant,
                        'cantidad_disponible': cant,
                        'fecha_adquision': date.today() - timedelta(days=60 - i*30),
                        'coste_unitario': Decimal(str(costo)),
                        'coste_final': Decimal(str(costo * cant)),
                        'producto': p,
                    }
                )
        self.stdout.write('  Inventario: OK')

        # Ventas de ejemplo (ultimos 30 dias)
        clientes_obj = list(Cliente.objects.all())
        for d in range(30):
            fecha_venta = date.today() - timedelta(days=d)
            n_ventas = random.randint(1, 4)
            for _ in range(n_ventas):
                cliente = random.choice(clientes_obj)
                empleado = random.choice(empleados)
                venta = NotaVenta.objects.create(
                    fecha=fecha_venta,
                    hora=time(random.randint(9, 19), random.randint(0, 59)),
                    monto_total=0, moneda='BOB', tipo_cambio=1,
                    cliente=cliente, empleado=empleado,
                )
                # 1-3 items
                items_seleccionados = random.sample(productos, random.randint(1, 3))
                for p, _costo in items_seleccionados:
                    cant = random.randint(1, 3)
                    lote = (Inventario.objects
                            .filter(producto=p, cantidad_disponible__gte=cant)
                            .order_by('fecha_adquision').first())
                    if lote:
                        DetalleVenta.objects.create(
                            concepto=p.nombre, cantidad=cant,
                            precio=p.precio_venta,
                            nota_venta=venta, inventario=lote,
                        )
                venta.calcular_total()
        self.stdout.write('  Ventas demo: OK')

        # Cliente demo con login para la tienda online
        demo_user, created = User.objects.get_or_create(
            username='cliente',
            defaults={'email': 'cliente@demo.bo', 'first_name': 'Cliente', 'last_name': 'Demo'}
        )
        if created:
            demo_user.set_password('cliente123')
            demo_user.save()
        # Vincular al primer cliente existente
        primer_cliente = Cliente.objects.first()
        if primer_cliente and not primer_cliente.user:
            primer_cliente.user = demo_user
            primer_cliente.save()
        self.stdout.write('  Usuario demo de tienda: cliente / cliente123')

        # Convertir el segundo cliente en mayorista
        clientes_list = list(Cliente.objects.all())
        if len(clientes_list) >= 2:
            clientes_list[1].tipo = 'mayorista'
            clientes_list[1].save()
            self.stdout.write(f'  Cliente "{clientes_list[1].persona.nombre}" marcado como MAYORISTA')

        self.stdout.write(self.style.SUCCESS('\nDatos demo cargados exitosamente.'))
        self.stdout.write('Ingresa con tu superusuario al ERP en /')
        self.stdout.write('O entra a la tienda online en /tienda/ con cliente / cliente123')
