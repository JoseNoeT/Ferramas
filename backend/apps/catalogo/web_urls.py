from django.urls import path

from apps.catalogo import views

urlpatterns = [
    path("ofertas/", views.ofertas_view, name="ofertas"),
]
