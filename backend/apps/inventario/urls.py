from django.urls import path

from apps.inventario.views import stock_disponible_producto_view

urlpatterns = [
    path(
        "productos/<int:producto_id>/stock-disponible/",
        stock_disponible_producto_view,
        name="api_stock_disponible_producto",
    ),
]
