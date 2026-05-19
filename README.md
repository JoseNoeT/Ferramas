# FERREMAX / FERREMAS

Sistema de ecommerce para ferretería y materiales de construcción, desarrollado como proyecto académico para la asignatura **ASY5131 Integración de Plataformas**.

---

## 1. Descripción general

FERREMAX es una plataforma de venta online orientada al rubro ferretero y de la construcción. El sistema cubre el ciclo completo de venta, desde el catálogo público hasta el pago con Webpay Plus, incluyendo roles internos, gestión de inventario, fidelización de clientes y servicios para el segmento Maestro/PYME.

- **Backend**: Django con Django REST Framework
- **Frontend**: Django Templates con HTML, CSS y JS modulares (sin frameworks externos)
- **Integración de pago**: Webpay Plus SDK (ambiente integration/testing)
- **Integración de indicadores**: mindicador.cl vía API REST
- **Base de datos**: SQLite (local y PythonAnywhere Free) / PostgreSQL (stack objetivo para producción)
- **Roles**: Público, Cliente, Maestro/PYME, Vendedor, Bodeguero, Contador, Administrador

---

## 2. Objetivos del sistema

| Objetivo | Descripción |
|----------|-------------|
| Venta online | Catálogo, carrito, checkout y pago integrado |
| Gestión de productos | CRUD de productos y categorías desde panel admin |
| Trazabilidad por roles | Cada rol ve y opera solo lo que le corresponde |
| Flujo de pedidos | Aprobación (vendedor) → Preparación (bodeguero) → Despacho/Retiro |
| Fidelización | Sistema de puntos FERREMAS acumulables por compra |
| Maestro/PYME | Perfil comercial, publicación de servicios, FerreCrédito |
| Indicadores económicos | UF, dólar, euro y UTM en tiempo real desde mindicador.cl |
| Encuestas | Encuestas de satisfacción post-pedido |
| Paneles internos | Vistas protegidas por rol para gestión operativa |

---

## 3. Stack tecnológico

| Componente | Tecnología |
|------------|-----------|
| Lenguaje | Python 3.13 |
| Framework web | Django 5.x |
| API REST | Django REST Framework |
| Autenticación JWT (base) | djangorestframework-simplejwt |
| CORS | django-cors-headers |
| Pagos | Transbank SDK (Webpay Plus) |
| Indicadores | requests → mindicador.cl |
| Config de entorno | python-decouple |
| Base de datos local/demo | SQLite |
| Base de datos producción | PostgreSQL (opcional) |
| Frontend | Django Templates + CSS/JS propios (sin React ni Vue) |
| Deploy | PythonAnywhere Free / Render / Railway / VPS |

---

## 4. Arquitectura general

```
Ferramas/
├── backend/                    # Django project root
│   ├── manage.py
│   ├── core/                   # Configuración global
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── apps/
│   │   ├── usuarios/           # Auth, roles, paneles admin/contador
│   │   ├── catalogo/           # Productos, categorías, seed_demo
│   │   ├── pedidos/            # Carrito, checkout, flujo vendedor/bodeguero
│   │   ├── pagos/              # Webpay Plus (initTransaction, commit, retorno)
│   │   ├── credito/            # FerreCrédito Maestro/PYME
│   │   ├── puntos/             # Puntos FERREMAS
│   │   ├── maestros/           # Perfiles y servicios Maestro/PYME
│   │   ├── encuestas/          # Encuestas de satisfacción
│   │   ├── integraciones/      # Proxy mindicador.cl
│   │   ├── inventario/         # API inventario
│   │   ├── reportes/           # API reportes
│   │   ├── autenticacion/      # JWT endpoints
│   │   └── notificaciones/     # Notificaciones internas
│   └── staticfiles/            # Generado por collectstatic (no en Git)
├── frontend/
│   ├── templates/              # Django Templates HTML
│   │   ├── base/               # base.html, head.html, navbar.html, scripts.html
│   │   ├── pages/              # home.html, catalogo.html, carrito.html, checkout.html...
│   │   ├── dashboard/          # administrador.html, vendedor.html, bodeguero.html, contador.html
│   │   └── components/         # hero.html, indicadores_economicos.html, franja_home_servicios.html...
│   └── static/
│       ├── css/
│       │   ├── global/         # variables.css, reset.css, base.css
│       │   ├── components/     # navbar.css, alerts.css, indicadores.css...
│       │   ├── pages/          # home.css, catalogo.css, carrito.css...
│       │   └── dashboard/      # administrador.css, vendedor.css, bodeguero.css
│       └── js/
│           ├── global/         # app.js
│           ├── components/     # alerts.js, navbar.js, indicadores.js
│           ├── pages/          # home.js, ofertas.js, registro-maestro-pyme.js
│           └── dashboard/      # vendedor.js
├── doc/                        # Documentación técnica del proyecto
├── requirements.txt
├── .env.example
└── README.md
```

**Convenciones de arquitectura:**
- `services.py` contiene la lógica de negocio de cada app; las vistas no acceden directamente a modelos.
- `views.py` coordina peticiones HTTP y delega en services.
- Los templates solo contienen estructura HTML y Django template tags — sin CSS ni JS embebido.
- CSS y JS se cargan desde `head.html` y `scripts.html` respectivamente como recursos externos.

---

## 5. Módulos principales

| App | Responsabilidad | Rol principal |
|-----|----------------|---------------|
| `usuarios` | Autenticación, registro, perfiles, paneles admin y contador | Todos |
| `catalogo` | Productos, categorías, catálogo público, panel admin productos | Admin, Público |
| `pedidos` | Carrito, checkout, flujo de pedidos, paneles vendedor/bodeguero | Cliente, Vendedor, Bodeguero |
| `pagos` | Integración Webpay Plus (init, commit, retorno, anulación) | Cliente |
| `credito` | FerreCrédito: cupo, saldo, solicitudes, panel admin | Maestro/PYME, Admin |
| `puntos` | Puntos FERREMAS: acumulación, consulta, panel admin | Cliente, Admin |
| `maestros` | Perfil Maestro/PYME, servicios publicados, panel admin | Maestro/PYME, Admin |
| `encuestas` | Encuestas post-pedido, respuestas, panel admin | Cliente, Admin |
| `integraciones` | Proxy a mindicador.cl (UF, dólar, euro, UTM) | Todos (API pública) |
| `inventario` | API de inventario | Admin, Bodeguero |
| `reportes` | API de reportes internos | Contador, Admin |
| `autenticacion` | Endpoints JWT (token/refresh) | API clients |
| `notificaciones` | Notificaciones internas entre roles | Interno |

---

## 6. Roles del sistema

| Rol | Acceso | Panel / Rutas principales | Usuario demo |
|-----|--------|--------------------------|--------------|
| **Público** | Catálogo, ofertas, Home, franja Maestro/PYME | `/`, `/catalogo/`, `/ofertas/` | Sin login |
| **Cliente** | Carrito, checkout, Webpay, puntos, encuestas, detalle producto | `/carrito/`, `/checkout/`, `/mis-puntos/` | `cliente@test.com` |
| **Maestro/PYME** | Todo lo de Cliente + perfil comercial, servicios, FerreCrédito | `/maestros/`, `/credito/`, `/servicios-maestros/` | `maestro@test.com` |
| **Vendedor** | Ver y gestionar pedidos entrantes (aprobar, rechazar, enviar a bodega) | `/dashboard/vendedor/` | `vendedor@test.com` |
| **Bodeguero** | Preparar pedidos, marcar listos para despacho/retiro | `/dashboard/bodeguero/` | `bodeguero@test.com` |
| **Contador** | Pagos, indicadores económicos, reportes | `/dashboard/contador/` | `contador@test.com` |
| **Administrador** | Gestión completa: productos, categorías, usuarios, maestros, crédito, puntos, encuestas | `/dashboard/admin/` | `admin.interno@test.com` |

---

## 7. Usuarios demo

Creados automáticamente por `seed_demo`. Se pueden usar inmediatamente después de ejecutar ese comando.

| Email | Contraseña | Rol interno | Acceso principal |
|-------|-----------|-------------|-----------------|
| `admin.interno@test.com` | `Test123456` | admin / superuser | Panel administrador completo |
| `vendedor@test.com` | `Test123456` | vendedor | Panel vendedor (pedidos) |
| `bodeguero@test.com` | `Test123456` | bodeguero | Panel bodeguero (preparación) |
| `contador@test.com` | `Test123456` | contador | Panel contador (pagos + indicadores) |
| `cliente@test.com` | `Test123456` | cliente | Ecommerce completo + puntos |
| `maestro@test.com` | `Test123456` | cliente con perfil Maestro/PYME aprobado | Servicios + FerreCrédito (cupo: $250.000) |

> `maestro@test.com` tiene rol `cliente` a nivel de modelo pero posee un `PerfilMaestroPyme` con estado `APROBADO` y una `CuentaCredito` activa con cupo de $250.000.

Ejecutar para crear o reutilizar:

```bash
python backend/manage.py seed_demo
```

---

## 8. Instalación local desde cero

### Windows (PowerShell)

```powershell
git clone https://github.com/JoseNoeT/Ferramas.git
cd Ferramas

python -m venv .venv
.\.venv\Scripts\activate

pip install --upgrade pip
pip install -r requirements.txt

copy .env.example backend\.env
# Editar backend\.env si se requiere (ver sección 9)

python backend/manage.py migrate
python backend/manage.py seed_demo
python backend/manage.py collectstatic --noinput
python backend/manage.py runserver
```

### Linux / macOS

```bash
git clone https://github.com/JoseNoeT/Ferramas.git
cd Ferramas

python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

cp .env.example backend/.env
# Editar backend/.env si se requiere (ver sección 9)

python backend/manage.py migrate
python backend/manage.py seed_demo
python backend/manage.py collectstatic --noinput
python backend/manage.py runserver
```

Abrir en el navegador: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

> **Nota:** `collectstatic` no es obligatorio en entorno local si `DEBUG=True`, ya que Django sirve archivos estáticos directamente desde `frontend/static/`.

---

## 9. Variables de entorno

Crear el archivo `backend/.env` copiando desde `.env.example`. Las variables más relevantes:

```env
# Clave secreta de Django (cambiar en producción)
DJANGO_SECRET_KEY=change-me-local-dev

# Modo debug (True en local, False en producción)
DEBUG=True

# Hosts permitidos (separados por coma)
ALLOWED_HOSTS=127.0.0.1,localhost

# Orígenes de confianza para CSRF (requerido en producción con HTTPS)
CSRF_TRUSTED_ORIGINS=

# Ruta personalizada de la base de datos SQLite (opcional en local)
# Ejemplo PythonAnywhere: /home/<usuario>/data/ferremax.sqlite3
SQLITE_PATH=

# Webpay Plus — credenciales de integration/testing (públicas, no usar en producción)
TRANSBANK_ENVIRONMENT=integration
TRANSBANK_COMMERCE_CODE=597055555532
TRANSBANK_API_KEY=579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C
```

> Las credenciales de Transbank incluidas son **públicas de testing** y están documentadas oficialmente por Transbank. No sustituyen credenciales reales de producción. El archivo `.env` está ignorado por Git.

---

## 10. Base de datos y persistencia

| Entorno | Motor | Ruta |
|---------|-------|------|
| Local | SQLite | `backend/db.sqlite3` (por defecto) |
| PythonAnywhere Free | SQLite persistente | `/home/<usuario>/data/ferremax.sqlite3` (via `SQLITE_PATH`) |
| Producción recomendada | PostgreSQL | Configurable vía `DATABASE_URL` (requiere ajuste en `settings.py`) |

**Comandos esenciales:**

```bash
# Aplicar migraciones (crea o actualiza tablas)
python backend/manage.py migrate

# Cargar datos demo (idempotente, se puede repetir sin duplicar)
python backend/manage.py seed_demo

# Backup manual SQLite
cp /home/<usuario>/data/ferremax.sqlite3 /home/<usuario>/data/backup_$(date +%F).sqlite3
```

> `db.sqlite3` no se sube a Git (está en `.gitignore`).

---

## 11. Datos demo con seed_demo

El comando `seed_demo` es **idempotente**: puede ejecutarse múltiples veces sin duplicar datos. Si un registro ya existe, lo actualiza/reutiliza.

Crea:
- 6 usuarios con roles y contraseñas fijas (ver sección 7)
- 4 categorías: Herramientas, Pinturas, Materiales Eléctricos, Seguridad
- 8 productos con stock, precio e imagen (URL Picsum)
- 1 perfil Maestro/PYME aprobado para `maestro@test.com`
- 3 servicios publicados por el maestro demo
- 1 cuenta FerreCrédito activa con cupo $250.000
- 1 cuenta de puntos con saldo inicial de 1.000 puntos para `cliente@test.com`

```bash
python backend/manage.py seed_demo
```

---

## 12. Ejecución del servidor

```bash
python backend/manage.py runserver
```

### URLs principales

| Ruta | Descripción |
|------|-------------|
| `http://127.0.0.1:8000/` | Home público con slider de productos |
| `http://127.0.0.1:8000/catalogo/` | Catálogo de productos |
| `http://127.0.0.1:8000/catalogo/<slug>/` | Detalle de producto |
| `http://127.0.0.1:8000/ofertas/` | Productos en oferta |
| `http://127.0.0.1:8000/login/` | Inicio de sesión |
| `http://127.0.0.1:8000/registro/` | Registro de cliente |
| `http://127.0.0.1:8000/carrito/` | Carrito de compras |
| `http://127.0.0.1:8000/checkout/` | Checkout y pago |
| `http://127.0.0.1:8000/dashboard/admin/` | Panel administrador |
| `http://127.0.0.1:8000/dashboard/vendedor/` | Panel vendedor |
| `http://127.0.0.1:8000/dashboard/bodeguero/` | Panel bodeguero |
| `http://127.0.0.1:8000/dashboard/contador/` | Panel contador |
| `http://127.0.0.1:8000/api/health/` | Healthcheck API |
| `http://127.0.0.1:8000/api/integraciones/indicadores/` | Indicadores económicos (JSON) |
| `http://127.0.0.1:8000/admin/` | Django Admin (solo superuser) |

---

## 13. Flujos principales para probar

### A. Cliente — compra completa

1. Acceder a `/` sin login → ver catálogo y franja Maestro/PYME
2. Ir a `/login/` → ingresar con `cliente@test.com / Test123456`
3. Navegar a `/catalogo/` → ver productos con stock
4. Agregar producto al carrito desde el catálogo o desde el Home
5. Ir a `/carrito/` → revisar ítems
6. Ir a `/checkout/` → completar datos de envío
7. Pagar con Webpay (ver sección 14 para tarjeta de prueba)
8. Verificar confirmación del pedido
9. Revisar puntos en `/mis-puntos/`

### B. Maestro/PYME

1. Ingresar con `maestro@test.com / Test123456`
2. Verificar franja de servicios en el Home
3. Acceder a `/maestros/` para ver perfil y servicios propios
4. Revisar estado de FerreCrédito en `/credito/`
5. Verificar que sus servicios aparecen en la franja del Home

### C. Administrador

1. Ingresar con `admin.interno@test.com / Test123456`
2. Panel principal: `/dashboard/admin/`
3. Gestionar productos: `/dashboard/admin/productos/`
4. Gestionar categorías: `/dashboard/admin/categorias/`
5. Gestionar usuarios: `/dashboard/admin/usuarios/`
6. Gestionar maestros, crédito, puntos y encuestas desde el panel

### D. Vendedor

1. Ingresar con `vendedor@test.com / Test123456`
2. Panel: `/dashboard/vendedor/`
3. Ver pedidos pendientes de aprobación
4. Aprobar o rechazar pedidos; enviar aprobados a bodega

### E. Bodeguero

1. Ingresar con `bodeguero@test.com / Test123456`
2. Panel: `/dashboard/bodeguero/`
3. Ver pedidos asignados desde vendedor
4. Poner en preparación y marcar listos para despacho/retiro

### F. Contador

1. Ingresar con `contador@test.com / Test123456`
2. Panel: `/dashboard/contador/`
3. Revisar historial de pagos y reportes
4. Consultar indicadores económicos en tiempo real (UF, dólar, euro, UTM)

---

## 14. Webpay Plus — testing

El sistema opera en **ambiente integration** de Transbank. No se procesan cobros reales.

### Tarjeta de crédito — transacción aprobada

| Campo | Valor |
|-------|-------|
| Número de tarjeta | `4051 8856 0044 6623` |
| CVV | `123` |
| Fecha de vencimiento | Cualquier fecha futura |
| RUT titular | `11.111.111-1` |
| Clave de internet | `123` |

### Tarjeta de débito — transacción rechazada

| Campo | Valor |
|-------|-------|
| Número de tarjeta | `5186 0595 5959 0568` |
| CVV | `123` |
| Fecha de vencimiento | Cualquier fecha futura |

> **Importante:** Nunca ingresar tarjetas reales en el ambiente integration. Las credenciales de Transbank configuradas en `.env.example` son públicas y sirven exclusivamente para pruebas.

---

## 15. Integración mindicador.cl

El sistema consulta la API pública de [mindicador.cl](https://mindicador.cl) para obtener indicadores económicos en tiempo real.

**Endpoint interno:**

```
GET /api/integraciones/indicadores/
```

**Respuesta esperada:**

```json
{
  "uf": 38500.00,
  "dolar": 950.00,
  "euro": 1040.00,
  "utm": 68500.00,
  "fecha_consulta": "2026-01-15T10:30:00",
  "fuente": "mindicador.cl"
}
```

**Dónde se muestra:**
- Widget en el Home (sección indicadores económicos)
- Panel del Contador (`/dashboard/contador/`)

Los valores son **informativos** y no modifican precios ni pagos dentro del sistema.

---

## 16. Frontend y reglas de arquitectura

### Separación de responsabilidades

| Capa | Ubicación | Regla |
|------|-----------|-------|
| HTML | `frontend/templates/` | Solo estructura, clases BEM y Django template tags |
| CSS | `frontend/static/css/` | Todo el estilo, cero `style=""` en templates |
| JS | `frontend/static/js/` | Toda la interactividad, cero `<script>` inline |

**Reglas estrictas:**
- Prohibido `<style>`, `style=""`, `<script>` inline, `onclick=`, `onchange=`, `onsubmit=` en templates.
- CSS global cargado desde `base/head.html`.
- JS global cargado desde `base/scripts.html`.
- JS específico de página cargado via `{% block page_scripts %}` en cada template.
- Excepción documentada: `style="width: {{ valor }}%"` en barras de progreso dinámicas (valor no puede expresarse como clase estática).

### Componentes visuales implementados

| Componente | Descripción |
|-----------|-------------|
| Navbar por roles | Muestra opciones según el rol del usuario autenticado |
| Slider de productos destacados | Marquee CSS continuo con pausa en hover, scroll en mobile |
| Franja Maestro/PYME | Muestra servicios aprobados del segmento en el Home |
| Widget de indicadores económicos | UF, dólar, euro, UTM desde mindicador.cl con botón de actualizar |
| Sistema de alertas | Mensajes Django (`messages`) renderizados con clases BEM |

---

## 17. Deploy en PythonAnywhere Free

Ver guía detallada: [`doc/DEPLOY_PYTHONANYWHERE_FREE.md`](doc/DEPLOY_PYTHONANYWHERE_FREE.md)

**Resumen de pasos:**

```bash
# En la consola Bash de PythonAnywhere
git clone https://github.com/JoseNoeT/Ferramas.git
cd Ferramas

python -m venv ~/.virtualenvs/ferremax
source ~/.virtualenvs/ferremax/bin/activate
pip install -r requirements.txt

mkdir -p /home/<usuario>/data

# Crear backend/.env con los valores del hosting (ver sección 9)
# DEBUG=False, ALLOWED_HOSTS=<usuario>.pythonanywhere.com, SQLITE_PATH=/home/<usuario>/data/ferremax.sqlite3

python backend/manage.py migrate
python backend/manage.py seed_demo
python backend/manage.py collectstatic --noinput
```

**Configuración Web App:**
- Manual configuration → Python 3.x compatible
- Virtualenv: `/home/<usuario>/.virtualenvs/ferremax`
- Working directory: `/home/<usuario>/Ferramas/backend`
- WSGI: apuntar a `core.wsgi` con `sys.path` incluyendo `/home/<usuario>/Ferramas/backend`
- Static files: URL `/static/` → Path `/home/<usuario>/Ferramas/backend/staticfiles`

---

## 18. Deploy genérico (Render / Railway / VPS)

Aplica para cualquier hosting que soporte Python WSGI.

```bash
# 1. Clonar y preparar
git clone https://github.com/JoseNoeT/Ferramas.git
cd Ferramas
pip install -r requirements.txt

# 2. Configurar variables de entorno (ver sección 9)
# DEBUG=False, ALLOWED_HOSTS=tu-dominio.com, CSRF_TRUSTED_ORIGINS=https://tu-dominio.com

# 3. Aplicar migraciones y cargar datos
python backend/manage.py migrate
python backend/manage.py seed_demo
python backend/manage.py collectstatic --noinput

# 4. Ejecutar con gunicorn (incluido en requirements.txt)
gunicorn core.wsgi:application --chdir backend --bind 0.0.0.0:8000
```

**Consideraciones:**
- Configurar variables de entorno según la plataforma (no subir `.env`).
- Para PostgreSQL: ajustar `DATABASES` en `settings.py` o usar `DATABASE_URL`.
- No subir `db.sqlite3` ni `staticfiles/` a Git.
- Los archivos estáticos deben ser servidos por el servidor web (nginx, caddy) o configurar WhiteNoise en `settings.py` si el hosting lo requiere.

---

## 19. Comandos útiles

| Comando | Descripción |
|---------|-------------|
| `python backend/manage.py check` | Verifica la configuración del proyecto |
| `python backend/manage.py migrate` | Aplica migraciones pendientes |
| `python backend/manage.py makemigrations` | Crea nuevas migraciones tras cambios en modelos |
| `python backend/manage.py seed_demo` | Crea/actualiza datos demo (idempotente) |
| `python backend/manage.py collectstatic --noinput` | Reúne archivos estáticos en `staticfiles/` |
| `python backend/manage.py runserver` | Inicia servidor de desarrollo en `127.0.0.1:8000` |
| `python backend/manage.py shell` | Abre la shell interactiva de Django |
| `python backend/manage.py createsuperuser` | Crea un superusuario manualmente |

> Todos los comandos se ejecutan desde la raíz del repositorio. En Windows: `.\.venv\Scripts\activate` antes de ejecutarlos, o usar `.\.venv\Scripts\python.exe backend\manage.py <comando>`.

---

## 20. Solución de problemas

| Error | Causa probable | Solución |
|-------|---------------|----------|
| `DisallowedHost` | Host no incluido en `ALLOWED_HOSTS` | Agregar el dominio en `backend/.env` → `ALLOWED_HOSTS=mi-dominio.com` |
| `ModuleNotFoundError: No module named 'core'` | Comando ejecutado fuera del contexto correcto | Ejecutar desde la raíz con `python backend/manage.py` o `cd backend && python manage.py` |
| Los archivos estáticos no cargan | `collectstatic` no ejecutado o `STATIC_ROOT` incorrecto | Ejecutar `python backend/manage.py collectstatic --noinput` |
| Base de datos vacía / sin tablas | `migrate` no ejecutado | Ejecutar `python backend/manage.py migrate` |
| Webpay no retorna al sitio | `CSRF_TRUSTED_ORIGINS` no configurado en producción | Agregar `CSRF_TRUSTED_ORIGINS=https://tu-dominio.com` en `.env` |
| mindicador falla o muestra `N/D` | API externa no disponible o sin conexión | Verificar conectividad; el widget muestra mensaje de error automáticamente |
| No aparecen productos en el Home | Base de datos vacía o productos inactivos | Ejecutar `seed_demo`; verificar que los productos tengan `activo=True` |
| No aparecen servicios Maestro/PYME | Perfil sin estado `APROBADO` o sin servicios | Ejecutar `seed_demo` o aprobar el perfil desde el panel admin |
| `CSRF verification failed` | Formulario enviado desde dominio no confiado | Agregar el dominio a `CSRF_TRUSTED_ORIGINS` en `.env` |

---

## 21. Estado del proyecto

### Implementado y commiteado

- [x] Ecommerce base: catálogo, carrito, checkout, confirmación
- [x] Roles y autenticación: login único por rol con redirección a panel correspondiente
- [x] Webpay Plus en ambiente integration/testing
- [x] Integración mindicador.cl (UF, dólar, euro, UTM)
- [x] Franja de servicios Maestro/PYME en el Home
- [x] Widget de indicadores económicos (Home y Panel contador)
- [x] Slider de productos destacados (CSS marquee, pausa hover, scroll mobile)
- [x] seed_demo idempotente con 6 usuarios, productos, servicios y cuentas
- [x] Paleta visual industrial (variables CSS)
- [x] Separación CSS/JS crítica en templates (sin CSS/JS embebido)
- [x] Configuración lista para PythonAnywhere Free
- [x] FerreCrédito Maestro/PYME (cupo, saldo, panel admin)
- [x] Sistema de puntos FERREMAS
- [x] Encuestas de satisfacción
- [x] Navbar diferenciada por rol

### Deuda técnica pendiente

- [ ] Refactor de `style=""` en dashboards (bodeguero, contador, vendedor) → mover a CSS
- [ ] Eliminar archivos CSS/JS vacíos huérfanos (`buttons.css`, `modal.js`, etc.)
- [ ] Conectar `vendedor.js` al template `vendedor.html` (archivo JS existe pero no se carga)
- [ ] Notificaciones por email cliente/maestro (lógica de negocio pendiente)
- [ ] Credenciales Webpay de producción real (requiere cuenta Transbank activa)
- [ ] Configuración PostgreSQL para producción escalable

---

## 22. Licencia / uso académico

Este proyecto es de carácter **exclusivamente académico**, desarrollado para la asignatura **ASY5131 Integración de Plataformas** del Duoc UC.

No está destinado a uso comercial. Las credenciales de Webpay incluidas son públicas de ambiente testing y no representan cuentas reales. Los datos de usuarios demo son ficticios.
