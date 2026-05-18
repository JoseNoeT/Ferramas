# DEPLOY PYTHONANYWHERE FREE - FERREMAX

## A. Objetivo
Desplegar FERREMAX en PythonAnywhere Free con SQLite persistente.

## B. Restricciones del plan Free
- 512 MiB de disco
- 1 web app
- 1 worker
- expiracion mensual
- MySQL no disponible en cuentas free nuevas
- uso de SQLite persistente

## C. Estructura esperada en servidor
- /home/<usuario>/Ferramas/
- /home/<usuario>/data/ferremax.sqlite3
- /home/<usuario>/.virtualenvs/ferremax/

## D. Comandos en Bash PythonAnywhere
```bash
git clone <repo>
cd Ferramas
python -m venv ~/.virtualenvs/ferremax
source ~/.virtualenvs/ferremax/bin/activate
pip install -r requirements.txt
mkdir -p /home/<usuario>/data
```

## E. Archivo .env de ejemplo
```env
DEBUG=False
ALLOWED_HOSTS=<usuario>.pythonanywhere.com
CSRF_TRUSTED_ORIGINS=https://<usuario>.pythonanywhere.com
SQLITE_PATH=/home/<usuario>/data/ferremax.sqlite3
TRANSBANK_ENVIRONMENT=integration
TRANSBANK_COMMERCE_CODE=597055555532
TRANSBANK_API_KEY=579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C
```

## F. Comandos Django
```bash
python backend/manage.py migrate
python backend/manage.py seed_demo
python backend/manage.py collectstatic --noinput
```

## G. Configuracion Web App PythonAnywhere
- Add new web app
- Manual configuration
- Python version compatible
- Virtualenv path:
  /home/<usuario>/.virtualenvs/ferremax
- Source code:
  /home/<usuario>/Ferramas
- Working directory:
  /home/<usuario>/Ferramas/backend

## H. WSGI sugerido
```python
import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
sys.path.insert(0, "/home/<usuario>/Ferramas/backend")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

## I. Static files
- URL: /static/
- Path: /home/<usuario>/Ferramas/backend/staticfiles

## J. Pruebas post-deploy
- /
- /catalogo/
- /api/integraciones/indicadores/
- login admin.interno@test.com
- login cliente@test.com
- login maestro@test.com
- carrito
- checkout
- franja Maestro/PYME
- Webpay testing

## K. Backup SQLite
```bash
cp /home/<usuario>/data/ferremax.sqlite3 /home/<usuario>/data/backup_ferremax_$(date +%F).sqlite3
```

## L. Actualizacion futura
```bash
git pull
source ~/.virtualenvs/ferremax/bin/activate
pip install -r requirements.txt
python backend/manage.py migrate
python backend/manage.py collectstatic --noinput
touch /var/www/<usuario>_pythonanywhere_com_wsgi.py
```

## Variables de entorno efectivas en settings.py
- DEBUG: configurable por DEBUG (compatibilidad con DJANGO_DEBUG)
- ALLOWED_HOSTS: configurable por ALLOWED_HOSTS (compatibilidad con DJANGO_ALLOWED_HOSTS)
- CSRF_TRUSTED_ORIGINS: configurable por entorno
- SQLITE_PATH: ruta SQLite configurable (por defecto backend/db.sqlite3)
- TRANSBANK_ENVIRONMENT, TRANSBANK_COMMERCE_CODE, TRANSBANK_API_KEY: configurables por entorno con fallback de integracion/testing
