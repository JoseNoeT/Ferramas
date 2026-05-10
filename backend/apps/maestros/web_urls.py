from django.urls import path

from apps.maestros.views import registro_maestro_pyme_view

urlpatterns = [
    path("registro/", registro_maestro_pyme_view, name="registro_maestro_pyme"),
]
