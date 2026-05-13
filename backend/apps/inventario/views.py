from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.catalogo.models import Producto


class VistaPlaceholder(viewsets.ViewSet):
    """ViewSet temporal de la app inventario."""

    # TODO: Reemplazar por ViewSets reales por recurso.
    pass


@api_view(["GET"])
@permission_classes([AllowAny])
def stock_disponible_producto_view(request, producto_id):
    producto = Producto.objects.filter(pk=producto_id, activo=True).first()
    if not producto:
        return Response({"detail": "Producto no encontrado."}, status=status.HTTP_404_NOT_FOUND)

    disponible = producto.stock > 0
    return Response(
        {
            "producto_id": producto.id,
            "nombre": producto.nombre,
            "activo": producto.activo,
            "stock_disponible": producto.stock,
            "disponible": disponible,
        },
        status=status.HTTP_200_OK,
    )

