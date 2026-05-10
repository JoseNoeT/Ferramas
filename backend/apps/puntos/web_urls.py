from django.urls import path

from apps.puntos.views import admin_puntos_view, mis_puntos_view

urlpatterns = [
    path("mis-puntos/", mis_puntos_view, name="mis_puntos"),
]

admin_urlpatterns = [
    path("", admin_puntos_view, name="admin_puntos"),
]
