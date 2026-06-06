from django.db import models

from apps.maestros.models import PerfilMaestroPyme


class CuentaCredito(models.Model):
	class Estado(models.TextChoices):
		ACTIVA = "activa", "Activa"
		BLOQUEADA = "bloqueada", "Bloqueada"
		CERRADA = "cerrada", "Cerrada"

	maestro = models.OneToOneField(
		PerfilMaestroPyme,
		on_delete=models.CASCADE,
		related_name="cuenta_credito",
	)
	cupo_aprobado = models.DecimalField(max_digits=12, decimal_places=2, default=0)
	saldo_usado = models.DecimalField(max_digits=12, decimal_places=2, default=0)
	estado = models.CharField(
		max_length=20,
		choices=Estado.choices,
		default=Estado.ACTIVA,
	)
	creado_en = models.DateTimeField(auto_now_add=True)
	actualizado_en = models.DateTimeField(auto_now=True)

	@property
	def saldo_disponible(self):
		return self.cupo_aprobado - self.saldo_usado

	class Meta:
		verbose_name = "Cuenta de Credito"
		verbose_name_plural = "Cuentas de Credito"
		ordering = ["-creado_en"]

	def __str__(self):
		return f"Cuenta credito de {self.maestro}"


class MovimientoCredito(models.Model):
	class Tipo(models.TextChoices):
		COMPRA = "compra", "Compra"
		ABONO = "abono", "Abono"
		AJUSTE = "ajuste", "Ajuste"

	cuenta = models.ForeignKey(
		CuentaCredito,
		on_delete=models.CASCADE,
		related_name="movimientos",
	)
	pedido = models.ForeignKey(
		"pedidos.Pedido",
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name="movimientos_credito",
	)
	tipo = models.CharField(max_length=20, choices=Tipo.choices)
	monto = models.DecimalField(max_digits=12, decimal_places=2)
	descripcion = models.CharField(max_length=255, blank=True)
	creado_en = models.DateTimeField(auto_now_add=True)

	class Meta:
		verbose_name = "Movimiento de Credito"
		verbose_name_plural = "Movimientos de Credito"
		ordering = ["-creado_en"]

	def __str__(self):
		return f"{self.get_tipo_display()} - {self.monto}"


class CuotaCredito(models.Model):
	class Estado(models.TextChoices):
		PENDIENTE = "pendiente", "Pendiente"
		PAGADA = "pagada", "Pagada"
		VENCIDA = "vencida", "Vencida"

	cuenta = models.ForeignKey(
		CuentaCredito,
		on_delete=models.CASCADE,
		related_name="cuotas",
	)
	pedido = models.ForeignKey(
		"pedidos.Pedido",
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name="cuotas_credito",
	)
	numero_cuota = models.PositiveIntegerField()
	total_cuotas = models.PositiveIntegerField()
	monto = models.DecimalField(max_digits=12, decimal_places=2)
	fecha_vencimiento = models.DateField()
	estado = models.CharField(
		max_length=20,
		choices=Estado.choices,
		default=Estado.PENDIENTE,
	)
	creado_en = models.DateTimeField(auto_now_add=True)

	class Meta:
		verbose_name = "Cuota de Credito"
		verbose_name_plural = "Cuotas de Credito"
		ordering = ["fecha_vencimiento", "numero_cuota"]

	def __str__(self):
		return f"Cuota {self.numero_cuota}/{self.total_cuotas} - {self.cuenta}"


class SolicitudFerreCredito(models.Model):
	class Estado(models.TextChoices):
		PENDIENTE = "pendiente", "Pendiente"
		APROBADA = "aprobada", "Aprobada"
		RECHAZADA = "rechazada", "Rechazada"

	maestro = models.ForeignKey(
		"maestros.PerfilMaestroPyme",
		on_delete=models.CASCADE,
		related_name="solicitudes_ferrecredito",
	)
	monto_solicitado = models.DecimalField(max_digits=10, decimal_places=2)
	motivo = models.TextField(blank=True, default="")
	estado = models.CharField(
		max_length=20,
		choices=Estado.choices,
		default=Estado.PENDIENTE,
	)
	cupo_aprobado = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	observacion_admin = models.TextField(blank=True, default="")
	creado_en = models.DateTimeField(auto_now_add=True)
	actualizado_en = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name = "Solicitud FerreCredito"
		verbose_name_plural = "Solicitudes FerreCredito"
		ordering = ["-creado_en"]

	def __str__(self):
		return f"Solicitud #{self.pk} - {self.maestro.usuario.email} ({self.get_estado_display()})"
