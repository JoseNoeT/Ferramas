from django.db import transaction

from apps.maestros.models import PerfilMaestroPyme, ServicioMaestro, SolicitudAsesoria


@transaction.atomic
def registrar_maestro_pyme(usuario, datos):
	"""Crea o actualiza el perfil Maestro/PYME con estado pendiente."""
	perfil, _ = PerfilMaestroPyme.objects.update_or_create(
		usuario=usuario,
		defaults={
			"tipo": datos.get("tipo"),
			"rut": datos.get("rut"),
			"rubro": datos.get("rubro"),
			"oficio": datos.get("oficio", ""),
			"nombre_empresa": datos.get("nombre_empresa", ""),
			"telefono": datos.get("telefono"),
			"direccion": datos.get("direccion"),
			"estado": PerfilMaestroPyme.Estado.PENDIENTE,
		},
	)
	return perfil


@transaction.atomic
def aprobar_maestro_pyme(perfil):
	"""Marca un perfil Maestro/PYME como aprobado."""
	perfil.estado = PerfilMaestroPyme.Estado.APROBADO
	perfil.save(update_fields=["estado", "actualizado_en"])
	return perfil


@transaction.atomic
def rechazar_maestro_pyme(perfil):
	"""Marca un perfil Maestro/PYME como rechazado."""
	perfil.estado = PerfilMaestroPyme.Estado.RECHAZADO
	perfil.save(update_fields=["estado", "actualizado_en"])
	return perfil


@transaction.atomic
def crear_servicio_maestro(perfil, datos):
	"""Crea un servicio para un perfil Maestro/PYME aprobado."""
	if perfil.estado != PerfilMaestroPyme.Estado.APROBADO:
		raise ValueError("El perfil debe estar aprobado para crear servicios.")

	servicio = ServicioMaestro.objects.create(
		maestro=perfil,
		titulo=datos.get("titulo"),
		descripcion=datos.get("descripcion"),
		rubro=datos.get("rubro"),
		zona_atencion=datos.get("zona_atencion"),
		precio_referencial=datos.get("precio_referencial"),
	)
	return servicio


@transaction.atomic
def cambiar_estado_servicio(servicio, activo):
	"""Activa o desactiva un servicio de Maestro/PYME."""
	servicio.activo = bool(activo)
	servicio.save(update_fields=["activo", "actualizado_en"])
	return servicio


@transaction.atomic
def crear_solicitud_asesoria(cliente, servicio, datos):
	"""Crea una solicitud de asesoria para un servicio activo."""
	if not servicio.activo:
		raise ValueError("No se puede solicitar asesoria para un servicio inactivo.")

	solicitud = SolicitudAsesoria.objects.create(
		cliente=cliente,
		servicio=servicio,
		nombre_cliente=datos.get("nombre_cliente"),
		email_cliente=datos.get("email_cliente"),
		telefono_cliente=datos.get("telefono_cliente"),
		direccion_o_comuna=datos.get("direccion_o_comuna"),
		comentario=datos.get("comentario", ""),
		cargo_confirmacion=5000,
	)
	return solicitud
