from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class EncuestaSatisfaccion(models.Model):
	pedido = models.OneToOneField(
		"pedidos.Pedido",
		on_delete=models.CASCADE,
		related_name="encuesta_satisfaccion",
	)
	cliente = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="encuestas_satisfaccion",
	)
	calificacion = models.PositiveSmallIntegerField(
		validators=[MinValueValidator(1), MaxValueValidator(5)]
	)
	comentario = models.TextField(blank=True, default="")
	creado_en = models.DateTimeField(auto_now_add=True)

	class Meta:
		verbose_name = "Encuesta de satisfaccion"
		verbose_name_plural = "Encuestas de satisfaccion"
		ordering = ["-creado_en"]

	def __str__(self):
		return f"Encuesta pedido #{self.pedido_id} - {self.calificacion}/5"
