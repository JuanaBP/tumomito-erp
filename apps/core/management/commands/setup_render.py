"""
Comando: python manage.py setup_render
Inicializa la base de datos en el primer deploy:
- Crea superusuario admin desde variables de entorno
- Seedea datos demo si la BD esta vacia

Es idempotente: en deploys posteriores no rompe nada.
"""
import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Inicializa el proyecto en produccion (Render). Idempotente.'

    def handle(self, *args, **options):
        # 1. Crear superuser si no existe
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@tumomito.bo')

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(
                username=username, password=password, email=email
            )
            self.stdout.write(self.style.SUCCESS(f'Superuser "{username}" creado.'))
        else:
            self.stdout.write(f'Superuser "{username}" ya existe (skip).')

        # 2. Seedear datos demo solo si no hay productos
        from apps.inventario.models import Producto
        if Producto.objects.count() == 0:
            self.stdout.write('Sin datos: ejecutando seed_demo...')
            call_command('seed_demo')
        else:
            self.stdout.write(f'Ya hay {Producto.objects.count()} productos (skip seed).')

        self.stdout.write(self.style.SUCCESS('setup_render completado.'))
