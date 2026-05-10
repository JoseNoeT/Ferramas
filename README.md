# FERREMAS

Sistema academico desarrollado con Django para gestion comercial interna y venta online de FERREMAS.

Este repositorio queda preparado con una base Django REST para implementar webservices paso a paso en la asignatura ASY5131.

## Requisitos

- Python 3.13 o compatible
- pip

## Estructura del proyecto

```text
ferremas/
├── backend/
├── frontend/
├── doc/
└── requirements.txt
```

## Instalacion en otro PC

1. Clonar el repositorio:

```powershell
git clone <URL_DEL_REPOSITORIO>
cd ferremas
```

2. Crear entorno virtual:

```powershell
python -m venv .venv
```

3. Activar entorno virtual:

```powershell
.venv\Scripts\activate
```

4. Instalar dependencias:

```powershell
pip install -r requirements.txt
```

5. (Opcional) Crear archivo de entorno local:

```powershell
copy .env.example .env
```

6. Entrar al backend:

```powershell
cd backend
```

7. Aplicar migraciones:

```powershell
python manage.py migrate
```

8. Ejecutar servidor de desarrollo:

```powershell
python manage.py runserver
```

9. Abrir en navegador:

```text
http://127.0.0.1:8000/
```

## Healthcheck API

Con el servidor activo, probar:

```text
GET http://127.0.0.1:8000/api/health/
```

Respuesta esperada:

```json
{
	"status": "ok",
	"project": "FERREMAS API",
	"database": "sqlite",
	"message": "Entorno preparado para implementar webservices REST"
}
```

## Stack base actual

- Django
- Django REST Framework
- JWT con SimpleJWT (base)
- SQLite para desarrollo local
- Arquitectura por apps
- services.py para logica de negocio

## Arquitectura base corregida

El proyecto reutiliza apps existentes en espanol para evitar duplicidad de dominios.

Apps reales reutilizadas como base:

- usuarios (base para WS_Usuarios)
- catalogo (base para WS_Productos y WS_Categorias)
- pedidos (base para WS_Carrito y WS_Pedidos)

Apps de dominio en espanol:

- inventario
- pagos
- reportes
- autenticacion
- credito
- puntos
- maestros
- encuestas
- notificaciones
- integraciones

Regla aplicada: si el dominio ya existe en espanol, se reutiliza; solo se agregan apps nuevas cuando el dominio no existia.

Cada app REST queda con estructura minima: models.py, serializers.py, views.py, services.py, permissions.py, urls.py, admin.py, apps.py.

## Orden recomendado para implementar webservices manualmente

1. WS_Productos usando catalogo
2. WS_Categorias usando catalogo
3. WS_Carrito usando pedidos
4. WS_Pedidos usando pedidos
5. WS_Pagos usando pagos
6. WS_Inventario usando inventario
7. WS_Puntos usando puntos
8. WS_MaestroPYME usando maestros
9. WS_FerreCredito usando credito
10. WS_Encuestas usando encuestas
11. WS_Notificaciones usando notificaciones
12. WS_Reportes usando reportes

## Credenciales internas de prueba

Estas credenciales son de ejemplo para pruebas locales si ya existen en la base de datos:

- Admin: admin.interno@test.com / temporal123
- Vendedor: vendedor.interno@test.com / temporal123
- Bodeguero: bodeguero.interno@test.com / temporal123
- Contador: contador.interno@test.com / temporal123

## Modulos implementados

- Login unico por rol
- Registro de clientes
- Catalogo de productos
- Carrito y checkout
- Flujo interno de pedidos
- Dashboard admin de productos
- Dashboard admin de categorias
- Dashboard admin de usuarios internos
- Dashboard vendedor
- Dashboard bodeguero
- Dashboard contador

## Notas

- La configuracion actual usa SQLite para desarrollo.
- PostgreSQL queda como objetivo para version productiva.
- Los archivos estaticos se sirven desde Django en entorno local.
- Los webservices se implementaran manualmente uno a uno.