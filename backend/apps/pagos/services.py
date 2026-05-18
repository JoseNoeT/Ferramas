from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from uuid import uuid4

from django.conf import settings
from django.db import transaction
from django.urls import reverse
from django.utils import timezone

from apps.pagos.models import Pago
from apps.puntos import services as puntos_services


def _build_transbank_options():
	try:
		from transbank.common.integration_type import IntegrationType
		from transbank.common.options import WebpayOptions
	except ModuleNotFoundError as exc:
		raise RuntimeError(
			"transbank-sdk no esta instalado. Agrega dependencias e instala requirements."
		) from exc

	environment = (settings.TRANSBANK_ENVIRONMENT or "integration").lower()
	integration_type = (
		IntegrationType.TEST if environment == "integration" else IntegrationType.LIVE
	)

	return WebpayOptions(
		settings.TRANSBANK_COMMERCE_CODE,
		settings.TRANSBANK_API_KEY,
		integration_type,
	)


def _get_transaction_client():
	try:
		from transbank.webpay.webpay_plus.transaction import Transaction
	except ModuleNotFoundError as exc:
		raise RuntimeError(
			"transbank-sdk no esta instalado. Agrega dependencias e instala requirements."
		) from exc

	return Transaction(_build_transbank_options())


def _get_amount_from_pedido(pedido):
	monto = Decimal(getattr(pedido, "total_final", None) or getattr(pedido, "total", 0) or 0)
	if monto <= 0:
		raise ValueError("El monto del pedido debe ser mayor a 0 para pagar con Webpay.")
	return monto


def _new_buy_order(pedido_id):
	timestamp = int(timezone.now().timestamp())
	suffix = uuid4().hex[:4].upper()
	return f"PED-{pedido_id}-{timestamp}-{suffix}"[:64]


def _new_session_id(pedido_id):
	return f"SES-{pedido_id}-{uuid4().hex[:8]}"[:64]


def _extract_field(response, field):
	if isinstance(response, dict):
		return response.get(field)
	return getattr(response, field, None)


def _extract_transaction_date(response):
	value = _extract_field(response, "transaction_date")
	if isinstance(value, str):
		parsed = timezone.datetime.fromisoformat(value.replace("Z", "+00:00"))
		return parsed if timezone.is_aware(parsed) else timezone.make_aware(parsed)
	return value


def crear_transaccion_webpay(pedido, request):
	if not pedido:
		raise ValueError("Pedido invalido para iniciar pago Webpay.")

	pago_redirigido = (
		Pago.objects.filter(
			pedido=pedido,
			estado=Pago.Estado.REDIRIGIDO,
			medio_pago=Pago.MedioPago.WEBPAY,
		)
		.exclude(token_ws__isnull=True)
		.exclude(token_ws="")
		.order_by("-creado_en")
		.first()
	)
	if pago_redirigido and pago_redirigido.url_webpay:
		return pago_redirigido

	monto = _get_amount_from_pedido(pedido)
	buy_order = _new_buy_order(pedido.id)
	session_id = _new_session_id(pedido.id)
	return_url = request.build_absolute_uri(reverse("pagos:webpay_retorno"))

	pago = Pago.objects.create(
		pedido=pedido,
		monto=monto,
		estado=Pago.Estado.INICIADO,
		buy_order=buy_order,
		session_id=session_id,
	)

	amount_for_tbk = int(monto.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
	transaction_client = _get_transaction_client()
	response = transaction_client.create(buy_order, session_id, amount_for_tbk, return_url)

	token_ws = _extract_field(response, "token")
	url_webpay = _extract_field(response, "url")

	if not token_ws or not url_webpay:
		pago.estado = Pago.Estado.ERROR
		pago.raw_response = response if isinstance(response, dict) else {"response": str(response)}
		pago.save(update_fields=["estado", "raw_response", "actualizado_en"])
		raise ValueError("Transbank no devolvio token/url para redireccionar el pago.")

	pago.token_ws = token_ws
	pago.url_webpay = url_webpay
	pago.estado = Pago.Estado.REDIRIGIDO
	pago.save(update_fields=["token_ws", "url_webpay", "estado", "actualizado_en"])
	return pago


def marcar_pago_abortado_webpay(*, tbk_token=None, buy_order=None, session_id=None):
	queryset = Pago.objects.select_related("pedido").filter(medio_pago=Pago.MedioPago.WEBPAY)

	if tbk_token:
		queryset = queryset.filter(token_ws=tbk_token)
	elif buy_order and session_id:
		queryset = queryset.filter(buy_order=buy_order, session_id=session_id)
	elif buy_order:
		queryset = queryset.filter(buy_order=buy_order)
	else:
		return None

	pago = queryset.order_by("-creado_en").first()
	if not pago:
		return None

	if pago.estado in {Pago.Estado.AUTORIZADO, Pago.Estado.RECHAZADO, Pago.Estado.ERROR}:
		return pago

	with transaction.atomic():
		pago = Pago.objects.select_for_update().select_related("pedido").get(pk=pago.pk)
		if pago.estado in {Pago.Estado.AUTORIZADO, Pago.Estado.RECHAZADO, Pago.Estado.ERROR}:
			return pago
		pago.estado = Pago.Estado.RECHAZADO
		pago.pedido.payment_status = pago.pedido.PaymentStatus.RECHAZADO
		pago.raw_response = {
			"aborted": True,
			"tbk_token": tbk_token,
			"tbk_orden_compra": buy_order,
			"tbk_id_session": session_id,
		}
		pago.pedido.save(update_fields=["payment_status"])
		pago.save(update_fields=["estado", "raw_response", "actualizado_en"])

	return pago


def confirmar_transaccion_webpay(token_ws):
	if not token_ws:
		raise ValueError("token_ws es obligatorio para confirmar la transaccion.")

	pago = None
	try:
		with transaction.atomic():
			pago = Pago.objects.select_for_update().select_related("pedido").get(token_ws=token_ws)

			if pago.estado in {
				Pago.Estado.AUTORIZADO,
				Pago.Estado.RECHAZADO,
				Pago.Estado.ERROR,
			}:
				return pago

			transaction_client = _get_transaction_client()
			response = transaction_client.commit(token_ws)

			response_code = _extract_field(response, "response_code")
			authorization_code = _extract_field(response, "authorization_code")
			transaction_date = _extract_transaction_date(response)

			pago.raw_response = response if isinstance(response, dict) else {"response": str(response)}
			pago.response_code = response_code
			pago.authorization_code = authorization_code
			pago.transaction_date = transaction_date

			if response_code == 0:
				pago.estado = Pago.Estado.AUTORIZADO
				pago.pedido.payment_status = pago.pedido.PaymentStatus.PAGADO
				puntos_services.acumular_puntos_por_pedido(pago.pedido.usuario, pago.pedido)
			else:
				pago.estado = Pago.Estado.RECHAZADO
				pago.pedido.payment_status = pago.pedido.PaymentStatus.RECHAZADO

			pago.pedido.save(update_fields=["payment_status"])
			pago.save(
				update_fields=[
					"raw_response",
					"response_code",
					"authorization_code",
					"transaction_date",
					"estado",
					"actualizado_en",
				]
			)
			return pago
	except Pago.DoesNotExist as exc:
		raise ValueError("No existe un pago Webpay asociado al token recibido.") from exc
	except Exception:
		if pago:
			with transaction.atomic():
				pago = Pago.objects.select_for_update().select_related("pedido").get(pk=pago.pk)
				pago.estado = Pago.Estado.ERROR
				pago.pedido.payment_status = pago.pedido.PaymentStatus.ERROR
				pago.pedido.save(update_fields=["payment_status"])
				pago.save(update_fields=["estado", "actualizado_en"])
		raise
