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
from apps.personal.models import Empleado, Contrato, Login, Rol
from apps.clientes.models import Cliente
from apps.proveedores.models import Proveedor
from apps.inventario.models import Producto, Inventario, Categoria
from apps.compras.models import NotaCompra, DetalleCompra
from apps.ventas.models import NotaVenta, DetalleVenta


# Definicion de roles iniciales del sistema
ROLES_INICIALES = [
    {
        'codigo': 'administrador',
        'nombre': 'Administrador',
        'descripcion': 'Acceso total al sistema, gestiona usuarios y configuracion.',
        'es_admin': True,
        'modulos': [],  # ignorado porque es_admin=True
    },
    {
        'codigo': 'gerente',
        'nombre': 'Gerente',
        'descripcion': 'Acceso a operacion completa excepto gestion de usuarios.',
        'modulos': ['dashboard', 'pos', 'ventas', 'clientes', 'compras', 'proveedores',
                    'productos', 'categorias', 'inventario', 'tienda_admin', 'bitacora', 'reportes'],
    },
    {
        'codigo': 'vendedor',
        'nombre': 'Vendedor',
        'descripcion': 'Realiza ventas en el POS y gestiona clientes.',
        'modulos': ['dashboard', 'pos', 'ventas', 'clientes', 'productos', 'tienda_admin'],
    },
    {
        'codigo': 'cajero',
        'nombre': 'Cajero',
        'descripcion': 'Cobra ventas en el POS, ve clientes y productos.',
        'modulos': ['dashboard', 'pos', 'ventas', 'clientes', 'productos'],
    },
    {
        'codigo': 'almacenero',
        'nombre': 'Almacenero',
        'descripcion': 'Gestiona productos, categorias e inventario.',
        'modulos': ['dashboard', 'productos', 'categorias', 'inventario', 'compras'],
    },
    {
        'codigo': 'comprador',
        'nombre': 'Comprador',
        'descripcion': 'Gestiona compras y proveedores.',
        'modulos': ['dashboard', 'compras', 'proveedores', 'productos'],
    },
]

CATEGORIAS_INICIALES = [
    ('Hogar', 'bi-house-door', 'primary'),
    ('Tecnologia', 'bi-laptop', 'info'),
    ('Juguetes', 'bi-controller', 'warning'),
    ('Ropa', 'bi-bag', 'danger'),
    ('Belleza', 'bi-heart', 'danger'),
    ('Papeleria', 'bi-pencil', 'secondary'),
    ('Ferreteria', 'bi-tools', 'dark'),
    ('Alimentos', 'bi-cup-hot', 'success'),
    ('Bebidas', 'bi-cup-straw', 'success'),
    ('Otros', 'bi-three-dots', 'secondary'),
]


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

        # ROLES iniciales
        roles_creados = {}
        for rol_data in ROLES_INICIALES:
            rol, _ = Rol.objects.update_or_create(
                codigo=rol_data['codigo'],
                defaults={
                    'nombre': rol_data['nombre'],
                    'descripcion': rol_data['descripcion'],
                    'modulos': rol_data['modulos'],
                    'es_admin': rol_data.get('es_admin', False),
                    'activo': True,
                }
            )
            roles_creados[rol_data['codigo']] = rol
        self.stdout.write(f'  Roles: {len(roles_creados)} OK')

        # CATEGORIAS iniciales
        cat_objs = {}
        for i, (nombre, icono, color) in enumerate(CATEGORIAS_INICIALES):
            cat, _ = Categoria.objects.get_or_create(
                nombre=nombre,
                defaults={'icono': icono, 'color': color, 'orden': i, 'activo': True},
            )
            cat_objs[nombre] = cat
        self.stdout.write(f'  Categorias: {len(cat_objs)} OK')

        # Empleados con roles y usuarios (uno por cada rol no-admin)
        empleados_data = [
            # (nombre, ci, celular, email, codigo_rol, username, password)
            ('Juan Carlos Mendoza', '5847123', '70123456', 'juan@tumomito.bo', 'gerente', 'gerente', 'gerente123'),
            ('Maria Laura Vega', '6398745', '71987654', 'maria@tumomito.bo', 'vendedor', 'vendedor', 'vendedor123'),
            ('Pedro Antonio Roca', '4521098', '72345678', 'pedro@tumomito.bo', 'cajero', 'cajero', 'cajero123'),
            ('Sofia Elena Aliaga', '3987654', '73456789', 'sofia@tumomito.bo', 'almacenero', 'almacenero', 'almacen123'),
            ('Luis Fernando Vaca', '2876543', '74567890', 'luis@tumomito.bo', 'comprador', 'comprador', 'comprador123'),
        ]
        empleados = []
        for nombre, ci, cel, email, cod_rol, uname, pwd in empleados_data:
            persona, _ = Persona.objects.get_or_create(
                ci=ci,
                defaults={
                    'nombre': nombre, 'fecha_nacimiento': date(1990, 5, 15),
                    'nacionalidad': 'Boliviana', 'celular': cel, 'email': email,
                    'direccion': 'Av. Cristo Redentor #123',
                }
            )
            # User para acceder al sistema
            u, created = User.objects.get_or_create(
                username=uname,
                defaults={'email': email, 'first_name': nombre.split()[0], 'is_staff': True}
            )
            if created:
                u.set_password(pwd)
                u.save()
            emp, _ = Empleado.objects.get_or_create(
                persona=persona,
                defaults={
                    'telf_contacto': '76543210', 'nombre_contacto': 'Familiar',
                    'estado_civil': 'Soltero',
                    'rol': roles_creados.get(cod_rol),
                    'user': u, 'fecha_ingreso': date(2024, 1, 1),
                    'activo': True,
                }
            )
            # Si ya existia pero sin rol, actualizar
            if not emp.rol:
                emp.rol = roles_creados.get(cod_rol)
                emp.user = u
                emp.activo = True
                emp.save()
            empleados.append(emp)

        # Tambien vincular el superuser admin al rol Administrador
        admin_user = User.objects.filter(is_superuser=True).first()
        if admin_user and not hasattr(admin_user, 'empleado_perfil'):
            try:
                p_admin, _ = Persona.objects.get_or_create(
                    ci='ADMIN-0001',
                    defaults={
                        'nombre': 'Administrador del Sistema', 'fecha_nacimiento': date(1985, 1, 1),
                        'nacionalidad': 'Boliviana', 'celular': '70000000',
                        'email': admin_user.email or 'admin@tumomito.bo',
                    }
                )
                Empleado.objects.get_or_create(
                    persona=p_admin,
                    defaults={
                        'telf_contacto': '70000000', 'nombre_contacto': 'N/A',
                        'estado_civil': 'Soltero',
                        'rol': roles_creados.get('administrador'),
                        'user': admin_user, 'activo': True,
                    }
                )
            except Exception as e:
                self.stdout.write(f'  (admin link skipped: {e})')

        self.stdout.write(f'  Empleados con usuarios: {len(empleados)} OK')

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
                    'nombre': nombre, 'categoria': cat_objs.get(cat), 'subcategoria': subcat,
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
