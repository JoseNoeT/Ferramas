from django.urls import path

from apps.encuestas.views import (
    admin_encuestas_view,
    encuesta_satisfaccion_pedido_view,
    encuesta_satisfaccion_view,
)

urlpatterns = [
    path("satisfaccion/", encuesta_satisfaccion_view, name="encuesta_satisfaccion"),
    path(
        "satisfaccion/<int:pedido_id>/",
        encuesta_satisfaccion_pedido_view,
        name="encuesta_satisfaccion_pedido",
    ),
]

admin_urlpatterns = [
    path("", admin_encuestas_view, name="admin_encuestas"),
]
