from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheckView(APIView):
    """Endpoint simple para validar el entorno base de la API."""

    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response(
            {
                "status": "ok",
                "project": "FERREMAS API",
                "database": "sqlite",
                "message": "Entorno preparado para implementar webservices REST",
            }
        )
