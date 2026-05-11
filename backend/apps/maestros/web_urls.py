from django.urls import path

from apps.maestros.views import (
    admin_maestros_view,
    aprobar_maestro_pyme_admin_view,
    mis_servicios_maestro_view,
    panel_maestro_pyme_view,
    publicar_servicio_maestro_view,
    rechazar_maestro_pyme_admin_view,
    registro_maestro_pyme_view,
    solicitud_asesoria_maestro_detalle_view,
    solicitud_asesoria_maestro_view,
    servicios_maestros_view,
)

urlpatterns = [
    path("registro/", registro_maestro_pyme_view, name="registro_maestro_pyme"),
    path("panel/", panel_maestro_pyme_view, name="panel_maestro_pyme"),
    path("servicios/", servicios_maestros_view, name="servicios_maestros"),
    path(
        "servicios/publicar/",
        publicar_servicio_maestro_view,
        name="publicar_servicio_maestro",
    ),
    path(
        "servicios/mis-servicios/",
        mis_servicios_maestro_view,
        name="mis_servicios_maestro",
    ),
    path(
        "servicios/solicitar/",
        solicitud_asesoria_maestro_view,
        name="solicitud_asesoria_maestro",
    ),
    path(
        "servicios/<int:servicio_id>/solicitar/",
        solicitud_asesoria_maestro_detalle_view,
        name="solicitud_asesoria_maestro_detalle",
    ),
]

admin_urlpatterns = [
    path("", admin_maestros_view, name="admin_maestros"),
    path(
        "<int:pk>/aprobar/",
        aprobar_maestro_pyme_admin_view,
        name="admin_maestro_aprobar",
    ),
    path(
        "<int:pk>/rechazar/",
        rechazar_maestro_pyme_admin_view,
        name="admin_maestro_rechazar",
    ),
]
