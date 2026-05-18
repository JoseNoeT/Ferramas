from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.integraciones import services as integraciones_services


class VistaPlaceholder(viewsets.ViewSet):
    """ViewSet temporal de la app integraciones."""

    # TODO: Reemplazar por ViewSets reales por recurso.
    pass


@api_view(["GET"])
@permission_classes([AllowAny])
def indicadores_economicos_view(request):
    data = integraciones_services.consultar_indicadores_economicos()
    return Response(data, status=status.HTTP_200_OK)

