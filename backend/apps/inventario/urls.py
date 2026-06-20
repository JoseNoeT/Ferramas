from django.urls import path

from apps.inventario.views import stock_disponible_producto_view
from apps.inventario.views import ajustar_stock_view

urlpatterns = [
    path(
        "productos/<int:producto_id>/stock-disponible/",
        stock_disponible_producto_view,
        name="api_stock_disponible_producto",
    ),
    path("ajustar-stock/", ajustar_stock_view, name="ajustar_stock"),
]
