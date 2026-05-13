from django.urls import path

from apps.credito.views import (
    aprobar_solicitud_ferrecredito_admin_view,
    admin_credito_view,
    estado_ferrecredito_view,
    rechazar_solicitud_ferrecredito_admin_view,
    solicitud_ferrecredito_view,
)

urlpatterns = [
    path("solicitud/", solicitud_ferrecredito_view, name="solicitud_ferrecredito"),
    path("estado/", estado_ferrecredito_view, name="estado_ferrecredito"),
]

admin_urlpatterns = [
    path("", admin_credito_view, name="admin_credito"),
    path(
        "solicitudes/<int:pk>/aprobar/",
        aprobar_solicitud_ferrecredito_admin_view,
        name="admin_credito_aprobar",
    ),
    path(
        "solicitudes/<int:pk>/rechazar/",
        rechazar_solicitud_ferrecredito_admin_view,
        name="admin_credito_rechazar",
    ),
]
