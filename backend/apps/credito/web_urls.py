from django.urls import path

from apps.credito.views import (
    admin_credito_view,
    estado_ferrecredito_view,
    solicitud_ferrecredito_view,
)

urlpatterns = [
    path("solicitud/", solicitud_ferrecredito_view, name="solicitud_ferrecredito"),
    path("estado/", estado_ferrecredito_view, name="estado_ferrecredito"),
]

admin_urlpatterns = [
    path("", admin_credito_view, name="admin_credito"),
]
