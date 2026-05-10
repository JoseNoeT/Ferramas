from django.urls import path

from apps.maestros.views import (
    admin_maestros_view,
    mis_servicios_maestro_view,
    panel_maestro_pyme_view,
    publicar_servicio_maestro_view,
    registro_maestro_pyme_view,
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
]

admin_urlpatterns = [
    path("", admin_maestros_view, name="admin_maestros"),
]
