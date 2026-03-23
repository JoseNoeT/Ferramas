# FERREMAS

Sistema web desarrollado con Django para la gestion comercial interna y venta online de FERREMAS.

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

5. Entrar al backend:

```powershell
cd backend
```

6. Aplicar migraciones:

```powershell
python manage.py migrate
```

7. Ejecutar servidor de desarrollo:

```powershell
python manage.py runserver
```

8. Abrir en navegador:

```text
http://127.0.0.1:8000/
```

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
- Los archivos estaticos se sirven desde Django en entorno local.
- Si se despliega en produccion, conviene mover configuraciones sensibles como `SECRET_KEY` y `DEBUG` a variables de entorno.