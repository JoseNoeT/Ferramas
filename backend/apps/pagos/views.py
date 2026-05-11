from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


def _token_simulado(pedido_id):
    base = f"pedido-{pedido_id}" if pedido_id else "pedido-sin-id"
    return f"WBP-{base}-SIM"


class VistaPlaceholder(viewsets.ViewSet):
    """ViewSet temporal de la app pagos."""

    # TODO: Reemplazar por ViewSets reales por recurso.
    pass


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def webpay_iniciar_view(request):
    """Inicia un pago simulado de Webpay."""
    pedido_id = request.data.get("pedido_id")
    token = _token_simulado(pedido_id)
    return Response(
        {
            "ok": True,
            "mensaje": "Pago simulado iniciado.",
            "token": token,
            "url_retorno": "/api/pagos/webpay/retorno/",
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def webpay_retorno_view(request):
    """Confirma retorno simulado de Webpay."""
    token = request.data.get("token")
    if not token:
        return Response(
            {"ok": False, "mensaje": "Token requerido."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(
        {
            "ok": True,
            "mensaje": "Retorno Webpay simulado confirmado.",
            "token": token,
            "estado": "autorizado",
        },
        status=status.HTTP_200_OK,
    )

