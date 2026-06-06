from django.db import models

from apps.pedidos.models import Pedido


class Pago(models.Model):
	class MedioPago(models.TextChoices):
		WEBPAY = "webpay", "Webpay Plus"
		FERRECREDITO = "ferrecredito", "FerreCrédito"
		TIENDA = "tienda", "Pago en tienda"

	class Estado(models.TextChoices):
		INICIADO = "iniciado", "Iniciado"
		REDIRIGIDO = "redirigido", "Redirigido"
		AUTORIZADO = "autorizado", "Autorizado"
		RECHAZADO = "rechazado", "Rechazado"
		ERROR = "error", "Error"

	pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="pagos")
	medio_pago = models.CharField(
		max_length=20,
		choices=MedioPago.choices,
		default=MedioPago.WEBPAY,
	)
	monto = models.DecimalField(max_digits=12, decimal_places=2)
	estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.INICIADO)
	buy_order = models.CharField(max_length=64, unique=True)
	session_id = models.CharField(max_length=64)
	token_ws = models.CharField(max_length=128, unique=True, null=True, blank=True)
	url_webpay = models.URLField(blank=True, default="")
	response_code = models.IntegerField(null=True, blank=True)
	authorization_code = models.CharField(max_length=32, null=True, blank=True)
	transaction_date = models.DateTimeField(null=True, blank=True)
	raw_response = models.JSONField(null=True, blank=True)
	creado_en = models.DateTimeField(auto_now_add=True)
	actualizado_en = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-creado_en"]

	def __str__(self):
		return (
			f"Pago #{self.pk} pedido={self.pedido_id} "
			f"estado={self.estado} buy_order={self.buy_order}"
		)
