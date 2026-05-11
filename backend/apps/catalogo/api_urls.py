from django.urls import path

from apps.catalogo import views
from .api_views import (
    CategoriaListAPIView, ProductoListAPIView
)

urlpatterns = [
   path("", ProductoListAPIView.as_view(), name="api_productos_lista"),
    path("<int:pk>/", views.api_producto_detalle_view, name="api_productos_detalle"),
   path("categorias/", CategoriaListAPIView.as_view(), name="api_categorias_lista"),
]
