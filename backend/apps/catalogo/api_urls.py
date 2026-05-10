from django.urls import path

from .api_views import (
    CategoriaListAPIView, ProductoListAPIView
)

urlpatterns = [
   path("", ProductoListAPIView.as_view(), name="api_productos_lista"),
    path("categorias/", CategoriaListAPIView.as_view(), name="api_categorias_lista"),
]
