# TUMOMITO ERP

Sistema ERP web desarrollado en **Django 5** para la empresa importadora **TUMOMITO**, que centraliza ventas, compras, inventario por lotes (FIFO), clientes, proveedores, recursos humanos y bitácora del sistema. Diseñado para que la empresa modernice su operación, deje atrás los procesos manuales/obsoletos y recupere su posicionamiento incrementando la velocidad de venta y la trazabilidad del stock.

---

## Tabla de contenidos

1. [Características](#características)
2. [Stack tecnológico](#stack-tecnológico)
3. [Estructura del proyecto](#estructura-del-proyecto)
4. [Instalación paso a paso](#instalación-paso-a-paso)
5. [Configurar PostgreSQL (opcional)](#configurar-postgresql-opcional)
6. [Cargar datos de prueba](#cargar-datos-de-prueba)
7. [Uso del sistema](#uso-del-sistema)
8. [Mapeo a la base de datos original](#mapeo-a-la-base-de-datos-original)
9. [Solución a problemas comunes](#solución-a-problemas-comunes)

---

## Características

### Módulos
- **Dashboard** con KPIs, gráficos (Chart.js) de ventas por día y por categoría, top productos vendidos, alertas de stock bajo y últimas transacciones.
- **Punto de Venta (POS)** interactivo en JavaScript con búsqueda en vivo, carrito dinámico, descuento automático de stock por **FIFO** y confirmación con AJAX.
- **Gestión de Compras** con creación automática de lotes en inventario al confirmar la nota.
- **Inventario por lotes** con costo unitario, fechas de vencimiento y estrategia FIFO.
- **CRUD completo** de Clientes, Proveedores, Productos, Empleados y Contratos.
- **Bitácora automática** vía middleware que registra todas las acciones POST/PUT/DELETE.
- **Autenticación** con Django auth, login estilizado y logout seguro.
- **Panel de administración** Django personalizado con inlines.
- **🛒 Tienda Online (E-commerce)** completa para clientes finales:
  - Catálogo público con filtros, búsqueda y ordenamiento
  - Carrito en sesión persistente al login
  - Registro y login de clientes (separado del login de empleados)
  - Precios diferenciados **mayorista vs minorista** (descuento automático según tipo de cliente y cantidad mínima)
  - Checkout con dirección de envío y 3 métodos de pago (transferencia bancaria con comprobante, QR/Tigo Money, contra entrega)
  - Estados de pedido (pendiente → pagado → confirmado → preparando → enviado → entregado)
  - Cliente puede ver historial de pedidos con timeline visual
  - Admin desde el ERP confirma pagos → **genera NotaVenta y descuenta inventario FIFO automáticamente**

### Diferenciadores frente al sistema "obsoleto" anterior
- Búsqueda y filtrado en tiempo real en todas las listas.
- Gráficos en vivo en el dashboard.
- POS apto para venta rápida (1-2 clics por producto).
- Trazabilidad completa: cada venta queda asociada al lote exacto de inventario del cual salió.
- Multi-moneda en compras (BOB / USD / EUR / CNY) con tipo de cambio.

---

## Stack tecnológico

- **Backend:** Python 3.10+, Django 5.0
- **Base de datos:** SQLite (default, listo para usar) o PostgreSQL (recomendado para producción, schema ya definido en `baseD`)
- **Frontend:** Bootstrap 5, Bootstrap Icons, Chart.js, JavaScript vanilla (sin framework pesado)
- **Forms:** django-crispy-forms + crispy-bootstrap5
- **Imágenes:** Pillow
- **Reportes (futuro):** ReportLab, openpyxl

---

## Estructura del proyecto

```
tumomito_erp/
├── manage.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── tumomito/              # Configuración del proyecto
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── apps/                  # Apps modulares
│   ├── core/              # Persona, Estado, Turno + comando seed_demo
│   ├── personal/          # Empleado, Contrato, Login, Bitacora + middleware
│   ├── clientes/          # Cliente (hereda de Persona)
│   ├── proveedores/       # Proveedor (B2B)
│   ├── inventario/        # Producto + Inventario (lotes FIFO)
│   ├── compras/           # NotaCompra + DetalleCompra
│   ├── ventas/            # NotaVenta + DetalleVenta + POS interactivo
│   └── dashboard/         # KPIs y gráficos
│
├── templates/             # Templates compartidos
│   ├── layouts/base.html  # Layout general (sidebar + topbar)
│   ├── registration/login.html
│   └── (uno por app)
│
├── static/css/erp.css     # Diseño del ERP
└── media/                 # Imágenes de productos subidas
```

---

## Instalación paso a paso

### Requisitos previos
- Python 3.10 o superior
- pip
- (Opcional) PostgreSQL si vas a usarlo en lugar de SQLite

### 1. Descomprimir el proyecto y entrar a la carpeta

```bash
unzip tumomito_erp.zip
cd tumomito_erp
```

### 2. Crear y activar entorno virtual

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
source venv/Scripts/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Aplicar migraciones (crea la base de datos SQLite)

```bash
python manage.py makemigrations core personal clientes proveedores inventario compras ventas
python manage.py migrate
```

### 5. Crear un superusuario para acceder al sistema

```bash
python manage.py createsuperuser
```

Te pedirá:
- Username (ej. `admin`)
- Email (ej. `admin@tumomito.bo`)
- Password (mínimo 8 caracteres)

### 6. (Opcional pero recomendado) Cargar datos de prueba

```bash
python manage.py seed_demo
```

Esto crea: 3 empleados, 5 clientes, 4 proveedores, 12 productos en distintas categorías, 24 lotes de inventario y ~75 ventas distribuidas en los últimos 30 días para que el dashboard tenga datos.

### 7. Ejecutar el servidor

```bash
python manage.py runserver
```

Abrir en el navegador: **http://127.0.0.1:8000/**

Iniciar sesión con el superusuario creado en el paso 5.

---

## Configurar PostgreSQL (opcional)

Si querés usar PostgreSQL en lugar de SQLite (recomendado para producción y para usar el schema original `baseD`):

1. Crear la base de datos:
   ```sql
   CREATE DATABASE tumomito_db;
   CREATE USER tumomito_user WITH PASSWORD 'tu_password_seguro';
   GRANT ALL PRIVILEGES ON DATABASE tumomito_db TO tumomito_user;
   ```

2. Editar `tumomito/settings.py`, comentar la sección de SQLite y descomentar la de PostgreSQL:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'tumomito_db',
           'USER': 'tumomito_user',
           'PASSWORD': 'tu_password_seguro',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```

3. Ejecutar migraciones de nuevo:
   ```bash
   python manage.py migrate
   ```

---

## Cargar datos de prueba

```bash
python manage.py seed_demo
```

Después de correr esto, podés ingresar al dashboard y ver:
- Gráfico de ventas de los últimos 30 días.
- Gráfico de torta por categoría de producto.
- Top 5 productos más vendidos.
- Productos con stock bajo (umbral < 10 unidades).
- Tabla de últimas ventas.

---

## Uso del sistema

### Flujo típico

1. **Login** → te lleva al Dashboard.
2. **Compras → Nueva Compra**: seleccionás proveedor, cargás productos uno por uno, confirmás. Esto **automáticamente crea los lotes en inventario**.
3. **Inventario → Productos**: ver el catálogo, editar precios.
4. **Inventario → Stock por Lotes**: ver qué tenés disponible, costo unitario y valor total del inventario.
5. **Ventas → Punto de Venta**: la pantalla central del negocio.
   - Buscás un cliente.
   - Hacés clic en los productos para agregarlos al carrito.
   - Ajustás cantidades con `+ / -`.
   - Confirmás la venta y se descuenta de los lotes más antiguos primero (FIFO).
6. **Ventas → Notas de Venta**: ver el historial e imprimir comprobantes.
7. **Personal → Bitácora**: auditar quién hizo qué.

### Atajos URL

| URL | Función |
|-----|---------|
| `/` | Dashboard |
| `/ventas/pos/` | Punto de Venta |
| `/admin/` | Admin de Django (gestión avanzada) |

---

## Mapeo a la base de datos original

El proyecto respeta exactamente el schema entregado en el archivo `baseD`:

| Tabla SQL original | Modelo Django | App |
|--------------------|---------------|-----|
| `persona` | `core.Persona` | core |
| `estado` | `core.Estado` | core |
| `turno` | `core.Turno` | core |
| `empleado` | `personal.Empleado` (OneToOne con Persona) | personal |
| `cliente` | `clientes.Cliente` (OneToOne con Persona) | clientes |
| `proveedor` | `proveedores.Proveedor` | proveedores |
| `producto` | `inventario.Producto` | inventario |
| `inventario` | `inventario.Inventario` | inventario |
| `nota_compra` | `compras.NotaCompra` | compras |
| `detalle_compra` | `compras.DetalleCompra` | compras |
| `nota_venta` | `ventas.NotaVenta` | ventas |
| `detalle_venta` | `ventas.DetalleVenta` | ventas |
| `login` | `personal.Login` | personal |
| `bitacora` | `personal.Bitacora` | personal |
| `contrato` | `personal.Contrato` | personal |

La herencia `Persona → Empleado` y `Persona → Cliente` se implementa con `OneToOneField(primary_key=True)` que es el patrón Django equivalente a la herencia por PK compartido del SQL original.

---

## Solución a problemas comunes

### Error: "no such table: ..."
Faltan migraciones:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Error: "ImportError: No module named 'crispy_forms'"
No instalaste las dependencias:
```bash
pip install -r requirements.txt
```

### El POS no agrega productos
Verificá que tenés productos con stock disponible. Corre `seed_demo` para tener datos de prueba.

### El dashboard se ve vacío
Necesita ventas para mostrar gráficos. Corre `python manage.py seed_demo` o crea ventas manuales desde el POS.

### En Windows: error con Pillow
```bash
pip install --upgrade pip
pip install Pillow --no-cache-dir
```

### Cambiar la zona horaria o el idioma
Editar `tumomito/settings.py`:
```python
LANGUAGE_CODE = 'es-bo'  # o 'es-ar', 'es-mx', etc.
TIME_ZONE = 'America/La_Paz'  # cambiar según tu zona
```

---

## Despliegue en Render (gratis)

El proyecto ya viene preparado para deploy en **Render** (https://render.com), que ofrece web service gratis + PostgreSQL gratis 90 días.

### Paso 1: Subir a GitHub

```bash
# Dentro de la carpeta tumomito_erp/
git init
git add .
git commit -m "ERP TUMOMITO + tienda online - inicial"
```

Después en https://github.com/new creá un repositorio llamado por ejemplo `tumomito-erp` (puede ser público o privado), y conectalo:

```bash
git remote add origin https://github.com/TU-USUARIO/tumomito-erp.git
git branch -M main
git push -u origin main
```

### Paso 2: Crear cuenta en Render

1. Ir a https://render.com/ y registrarse con GitHub (es gratis, no pide tarjeta).
2. Autorizar a Render para acceder a tu repositorio.

### Paso 3: Deploy con Blueprint (un solo clic)

El proyecto incluye un archivo `render.yaml` que automatiza todo. En Render:

1. Click en **"New +"** → **"Blueprint"**.
2. Conectá el repo `tumomito-erp`.
3. Render detecta `render.yaml` y crea automáticamente:
   - **Base de datos PostgreSQL** llamada `tumomito-db`
   - **Web service** llamado `tumomito-erp`
   - Las variables de entorno (`SECRET_KEY`, `DATABASE_URL`, etc.) se configuran solas
4. Click en **"Apply"** y esperar 5-10 minutos al primer build.

### Paso 4: Crear superusuario y datos demo

Una vez deployado, abrí la **Shell** del web service en Render y ejecutá:

```bash
python manage.py createsuperuser
python manage.py seed_demo
```

### Paso 5: ¡Listo!

Abrí tu app en `https://tumomito-erp.onrender.com/`:
- `/login/` → ERP interno
- `/tienda/` → Tienda online pública

> **Nota sobre el free tier:** la app duerme después de 15 minutos sin tráfico y la primera petición tarda ~30 segundos en despertar. Para evitarlo, podés actualizar el web service a $7/mes.

### Variables de entorno

| Variable | Local (.env) | Producción (Render) |
|---|---|---|
| `DEBUG` | `True` | `False` |
| `SECRET_KEY` | Cualquier string | Render genera automático |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | `.onrender.com` |
| `DATABASE_URL` | (vacío = SQLite) | Render lo provee |

### Archivos relevantes para el deploy

- `requirements.txt` — Dependencias Python (incluye gunicorn, whitenoise, dj-database-url)
- `build.sh` — Script ejecutado por Render: instala deps + collectstatic + migrate
- `render.yaml` — Blueprint de Render: define web service y DB
- `.env.example` — Plantilla de variables de entorno para desarrollo local

### Alternativa: Despliegue en PythonAnywhere

Para un demo académico sin necesidad de Postgres, [PythonAnywhere](https://www.pythonanywhere.com/) ofrece hosting Django gratis (con MySQL). Es más simple pero limitado:
- Subdominio fijo `username.pythonanywhere.com`
- Solo MySQL en plan free (no PostgreSQL)
- Sin auto-deploy desde GitHub

Pasos: registrarse → "Web" → "Add new web app" → Manual config Python 3.12 → subir el código por consola → configurar WSGI apuntando a `tumomito.wsgi`.

---

## Próximas mejoras sugeridas

### Completadas
- [x] **E-commerce público para que los clientes compren online** ✅
  - Catálogo público con búsqueda y filtros
  - Carrito de compras en sesión
  - Registro/login de clientes (separado del personal)
  - Precios diferenciados mayorista vs minorista
  - Checkout con dirección y 3 métodos de pago
  - Estados de pedido con timeline visual
  - Generación automática de NotaVenta + descuento FIFO al confirmar

### Pendientes
- [ ] Generación de PDF para notas de venta con ReportLab
- [ ] Exportación a Excel de reportes con openpyxl
- [ ] Roles y permisos diferenciados (cajero, gerente, admin)
- [ ] Pasarela de pago real (MercadoPago Bolivia, Khipu, Tigo Money API)
- [ ] App móvil para vendedores en campo
- [ ] Integración con WhatsApp Business para confirmación de pedidos
- [ ] Dashboard de comparación mes a mes y año a año
- [ ] Alertas automáticas por email cuando hay stock crítico
- [ ] Notificación al cliente por email cuando cambia el estado del pedido
- [ ] Sistema de reseñas y valoraciones de productos
- [ ] Cupones de descuento y promociones
- [ ] Wishlist (lista de favoritos del cliente)

---

## Licencia y créditos

Sistema desarrollado como propuesta académica para la empresa **TUMOMITO**.  
Stack: Django + Bootstrap + Chart.js.

**Año:** 2026
