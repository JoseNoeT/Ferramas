from django.conf import settings
from django.db import models


class PerfilMaestroPyme(models.Model):
	class Tipo(models.TextChoices):
		MAESTRO = "maestro", "Maestro"
		PYME = "pyme", "PYME"

	class Estado(models.TextChoices):
		PENDIENTE = "pendiente", "Pendiente"
		APROBADO = "aprobado", "Aprobado"
		RECHAZADO = "rechazado", "Rechazado"

	usuario = models.OneToOneField(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="perfil_maestro_pyme",
	)
	tipo = models.CharField(max_length=20, choices=Tipo.choices)
	rut = models.CharField(max_length=20)
	rubro = models.CharField(max_length=100)
	oficio = models.CharField(max_length=100, blank=True)
	nombre_empresa = models.CharField(max_length=150, blank=True)
	telefono = models.CharField(max_length=30)
	direccion = models.CharField(max_length=255)
	estado = models.CharField(
		max_length=20,
		choices=Estado.choices,
		default=Estado.PENDIENTE,
	)
	descuento_primera_compra_usado = models.BooleanField(default=False)
	creado_en = models.DateTimeField(auto_now_add=True)
	actualizado_en = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name = "Perfil Maestro/PYME"
		verbose_name_plural = "Perfiles Maestro/PYME"
		ordering = ["-creado_en"]

	def __str__(self):
		return f"{self.usuario} ({self.get_tipo_display()})"


class ServicioMaestro(models.Model):
	maestro = models.ForeignKey(
		PerfilMaestroPyme,
		on_delete=models.CASCADE,
		related_name="servicios",
	)
	titulo = models.CharField(max_length=150)
	descripcion = models.TextField()
	rubro = models.CharField(max_length=100)
	zona_atencion = models.CharField(max_length=150)
	precio_referencial = models.DecimalField(
		max_digits=10,
		decimal_places=2,
		null=True,
		blank=True,
	)
	activo = models.BooleanField(default=True)
	creado_en = models.DateTimeField(auto_now_add=True)
	actualizado_en = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name = "Servicio Maestro"
		verbose_name_plural = "Servicios Maestro"
		ordering = ["-creado_en"]

	def __str__(self):
		return self.titulo


class SolicitudAsesoria(models.Model):
	class Estado(models.TextChoices):
		PENDIENTE = "pendiente", "Pendiente"
		CONFIRMADA = "confirmada", "Confirmada"
		CANCELADA = "cancelada", "Cancelada"

	cliente = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="solicitudes_asesoria",
	)
	servicio = models.ForeignKey(
		ServicioMaestro,
		on_delete=models.CASCADE,
		related_name="solicitudes",
	)
	nombre_cliente = models.CharField(max_length=150)
	email_cliente = models.EmailField()
	telefono_cliente = models.CharField(max_length=30)
	direccion_o_comuna = models.CharField(max_length=255)
	comentario = models.TextField(blank=True)
	cargo_confirmacion = models.PositiveIntegerField(default=5000)
	estado = models.CharField(
		max_length=20,
		choices=Estado.choices,
		default=Estado.PENDIENTE,
	)
	creado_en = models.DateTimeField(auto_now_add=True)

	class Meta:
		verbose_name = "Solicitud de Asesoria"
		verbose_name_plural = "Solicitudes de Asesoria"
		ordering = ["-creado_en"]

	def __str__(self):
		return f"{self.nombre_cliente} - {self.servicio.titulo}"
