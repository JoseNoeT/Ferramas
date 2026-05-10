from django.urls import path

from apps.encuestas.views import admin_encuestas_view, encuesta_satisfaccion_view

urlpatterns = [
    path("satisfaccion/", encuesta_satisfaccion_view, name="encuesta_satisfaccion"),
]

admin_urlpatterns = [
    path("", admin_encuestas_view, name="admin_encuestas"),
]
