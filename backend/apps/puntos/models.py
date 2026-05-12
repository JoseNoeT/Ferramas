from django.conf import settings
from django.db import models


class CuentaPuntos(models.Model):
	usuario = models.OneToOneField(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="cuenta_puntos",
	)
	saldo = models.PositiveIntegerField(default=0)
	creado_en = models.DateTimeField(auto_now_add=True)
	actualizado_en = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name = "Cuenta de puntos"
		verbose_name_plural = "Cuentas de puntos"

	def __str__(self):
		return f"Cuenta de puntos de {self.usuario}"


class MovimientoPuntos(models.Model):
	class Tipo(models.TextChoices):
		GANADO = "ganado", "Ganado"
		USADO = "usado", "Usado"
		AJUSTE = "ajuste", "Ajuste"

	cuenta = models.ForeignKey(
		CuentaPuntos,
		on_delete=models.CASCADE,
		related_name="movimientos",
	)
	pedido = models.ForeignKey(
		"pedidos.Pedido",
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name="movimientos_puntos",
	)
	tipo = models.CharField(max_length=20, choices=Tipo.choices)
	puntos = models.PositiveIntegerField()
	saldo_resultante = models.PositiveIntegerField()
	descripcion = models.CharField(max_length=255, blank=True, default="")
	creado_en = models.DateTimeField(auto_now_add=True)

	class Meta:
		verbose_name = "Movimiento de puntos"
		verbose_name_plural = "Movimientos de puntos"
		ordering = ["-creado_en"]

	def __str__(self):
		return f"{self.get_tipo_display()} {self.puntos} pts"
