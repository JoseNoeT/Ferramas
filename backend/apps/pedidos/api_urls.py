from django.urls import path

from apps.pedidos import views

urlpatterns = [
    path("", views.api_carrito_o_pedidos_root_view, name="api_carrito_o_pedidos_root"),
    path("agregar/", views.api_carrito_agregar_view, name="api_carrito_agregar"),
    path("eliminar/", views.api_carrito_eliminar_view, name="api_carrito_eliminar"),
    path("create/", views.api_pedidos_create_view, name="api_pedidos_create"),
]
