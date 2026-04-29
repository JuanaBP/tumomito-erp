#!/usr/bin/env bash
# build.sh: ejecutado por Render en cada deploy
set -o errexit  # Salir si algun comando falla

echo "==> Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt

echo "==> Recolectando archivos estaticos..."
python manage.py collectstatic --no-input

echo "==> Aplicando migraciones..."
python manage.py migrate --no-input

echo "==> Inicializando datos (admin + demo si BD vacia)..."
python manage.py setup_render

echo "==> Build completado."
