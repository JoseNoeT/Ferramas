from django.urls import path

from apps.integraciones import views

urlpatterns = [
    path("indicadores/", views.indicadores_economicos_view, name="indicadores_economicos"),
]
