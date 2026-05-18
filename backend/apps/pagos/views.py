from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt

from apps.pagos import services as pagos_services
from apps.pedidos.models import Pedido


@login_required
def iniciar_webpay_view(request, pedido_id):
    pedido = get_object_or_404(Pedido, pk=pedido_id, usuario=request.user)

    try:
        pago = pagos_services.crear_transaccion_webpay(pedido, request)
    except Exception as exc:
        messages.error(request, f"No se pudo iniciar Webpay: {exc}")
        return redirect("checkout")

    return render(
        request,
        "pages/webpay_redirect.html",
        {
            "url_webpay": pago.url_webpay,
            "token_ws": pago.token_ws,
            "pedido": pedido,
        },
    )


@csrf_exempt
def retorno_webpay_view(request):
    token_ws = request.POST.get("token_ws") or request.GET.get("token_ws")
    tbk_token = request.POST.get("TBK_TOKEN") or request.GET.get("TBK_TOKEN")
    tbk_orden_compra = request.POST.get("TBK_ORDEN_COMPRA") or request.GET.get("TBK_ORDEN_COMPRA")
    tbk_id_session = request.POST.get("TBK_ID_SESSION") or request.GET.get("TBK_ID_SESSION")

    if not token_ws:
        if tbk_token or tbk_orden_compra or tbk_id_session:
            pago = pagos_services.marcar_pago_abortado_webpay(
                tbk_token=tbk_token,
                buy_order=tbk_orden_compra,
                session_id=tbk_id_session,
            )
            if pago:
                messages.warning(request, "El pago Webpay fue cancelado o abortado.")
                return redirect("confirmacion", pk=pago.pedido_id)

        messages.error(request, "No se recibio token_ws de Webpay.")
        return redirect("checkout")

    try:
        pago = pagos_services.confirmar_transaccion_webpay(token_ws)
    except Exception as exc:
        messages.error(request, f"Error al confirmar Webpay: {exc}")
        return redirect("checkout")

    return redirect("confirmacion", pk=pago.pedido_id)

