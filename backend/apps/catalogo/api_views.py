from rest_framework import generics
from .models import Categoria, Producto

from .serializers import CategoriaSerializer, ProductoSerializers

class CategoriaListAPIView(generics.ListAPIView):
    serializer_class = CategoriaSerializer

    def get_queryset(self):
        return Categoria.objects.filter(activa=True)

class ProductoListAPIView(generics.ListAPIView):
    serializer_class = ProductoSerializers

    def get_queryset(self):
        return Producto.objects.filter(activo=True).select_related("categoria")     