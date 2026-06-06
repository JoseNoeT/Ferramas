from django.conf import settings
from django.db import models


class MovimientoInventario(models.Model):
	class TipoMovimiento(models.TextChoices):
		ENTRADA = "entrada", "Entrada"
		SALIDA = "salida", "Salida"
		RESERVA = "reserva", "Reserva"
		LIBERACION = "liberacion", "Liberacion"
		AJUSTE = "ajuste", "Ajuste"

	producto = models.ForeignKey(
		"catalogo.Producto",
		on_delete=models.CASCADE,
		related_name="movimientos_inventario",
	)
	pedido = models.ForeignKey(
		"pedidos.Pedido",
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name="movimientos_inventario",
	)
	tipo_movimiento = models.CharField(
		max_length=20,
		choices=TipoMovimiento.choices,
	)
	cantidad = models.PositiveIntegerField()
	stock_anterior = models.PositiveIntegerField()
	stock_nuevo = models.PositiveIntegerField()
	usuario = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name="movimientos_inventario",
	)
	motivo = models.CharField(max_length=255, blank=True, default="")
	fecha_creacion = models.DateTimeField(auto_now_add=True)

	class Meta:
		verbose_name = "Movimiento de Inventario"
		verbose_name_plural = "Movimientos de Inventario"
		ordering = ["-fecha_creacion"]

	def __str__(self):
		return (
			f"{self.get_tipo_movimiento_display()} - {self.producto.nombre} "
			f"({self.stock_anterior} -> {self.stock_nuevo})"
		)
