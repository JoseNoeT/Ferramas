"""Root URL configuration for FERREMAX backend."""

from apps.credito import web_urls as credito_web_urls
from apps.encuestas import web_urls as encuestas_web_urls
from apps.maestros import web_urls as maestros_web_urls
from apps.puntos import web_urls as puntos_web_urls
from django.contrib import admin
from django.urls import include, path

from core.api_views import HealthCheckView

urlpatterns = [
	path("admin/", admin.site.urls),
	path("", include("apps.usuarios.urls")),
	path("", include("apps.catalogo.urls")),
	path("", include("apps.catalogo.web_urls")),
	path("", include("apps.pedidos.urls")),
	path("maestros/", include(maestros_web_urls.urlpatterns)),
	path("credito/", include("apps.credito.web_urls")),
	path("puntos/", include("apps.puntos.web_urls")),
	path("encuestas/", include(encuestas_web_urls.urlpatterns)),
	path("dashboard/admin/maestros/", include(maestros_web_urls.admin_urlpatterns)),
	path("dashboard/admin/credito/", include(credito_web_urls.admin_urlpatterns)),
	path("dashboard/admin/puntos/", include(puntos_web_urls.admin_urlpatterns)),
	path("dashboard/admin/encuestas/", include(encuestas_web_urls.admin_urlpatterns)),
	path("api/health/", HealthCheckView.as_view(), name="api_health"),
	path("api/autenticacion/", include("apps.autenticacion.urls")),
	path("api/usuarios/", include("apps.usuarios.api_urls")),
	path("api/productos/", include("apps.catalogo.api_urls")),
	path("api/inventario/", include("apps.inventario.urls")),
	path("api/carrito/", include("apps.pedidos.api_urls")),
	path("api/pedidos/", include("apps.pedidos.api_urls")),
	path("api/pagos/", include("apps.pagos.urls")),
	path("api/credito/", include("apps.credito.urls")),
	path("api/puntos/", include("apps.puntos.urls")),
	path("api/maestros-pyme/", include("apps.maestros.urls")),
	path("api/encuestas/", include("apps.encuestas.urls")),
	path("api/notificaciones/", include("apps.notificaciones.urls")),
	path("api/reportes/", include("apps.reportes.urls")),
	path("api/integraciones/", include("apps.integraciones.urls")),
]
