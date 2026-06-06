from datetime import date
from decimal import Decimal

from django.db import transaction
from django.db.models import Q, Sum
from django.utils import timezone

from apps.credito.models import CuentaCredito, CuotaCredito, MovimientoCredito, SolicitudFerreCredito
from apps.maestros.models import PerfilMaestroPyme


def obtener_cuenta_credito_usuario(usuario):
	perfil = PerfilMaestroPyme.objects.filter(usuario=usuario).first()
	if not perfil or perfil.estado != PerfilMaestroPyme.Estado.APROBADO:
		return None

	return CuentaCredito.objects.filter(
		maestro=perfil,
		estado=CuentaCredito.Estado.ACTIVA,
	).first()


def tiene_cuotas_vencidas(cuenta):
	hoy = timezone.localdate()
	return CuotaCredito.objects.filter(cuenta=cuenta).filter(
		estado=CuotaCredito.Estado.VENCIDA,
	).exists() or CuotaCredito.objects.filter(
		cuenta=cuenta,
		estado=CuotaCredito.Estado.PENDIENTE,
		fecha_vencimiento__lt=hoy,
	).exists()


def validar_uso_ferrecredito(usuario, monto):
	perfil = PerfilMaestroPyme.objects.filter(usuario=usuario).first()
	if not perfil:
		raise ValueError("No tienes perfil Maestro/PYME asociado.")

	if perfil.estado != PerfilMaestroPyme.Estado.APROBADO:
		raise ValueError("Tu perfil Maestro/PYME no está aprobado para usar FerreCrédito.")

	cuenta = CuentaCredito.objects.filter(maestro=perfil).first()
	if not cuenta:
		raise ValueError("No tienes cuenta FerreCrédito activa. Solicita evaluación de crédito.")

	if cuenta.estado != CuentaCredito.Estado.ACTIVA:
		raise ValueError("Tu cuenta FerreCrédito no está activa.")

	if tiene_cuotas_vencidas(cuenta):
		raise ValueError("Tienes cuotas vencidas en FerreCrédito. Regulariza tu deuda para continuar.")

	monto_decimal = Decimal(str(monto or 0))
	if monto_decimal <= 0:
		raise ValueError("El monto a financiar con FerreCrédito debe ser mayor a 0.")

	if cuenta.saldo_disponible < monto_decimal:
		raise ValueError("No tienes cupo disponible suficiente en FerreCrédito.")

	return cuenta


def _sumar_meses(fecha_base, meses):
	month = fecha_base.month - 1 + meses
	year = fecha_base.year + month // 12
	month = month % 12 + 1
	day = min(
		fecha_base.day,
		[31, 29 if (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1],
	)
	return date(year, month, day)


@transaction.atomic
def registrar_compra_ferrecredito(cuenta, pedido=None, monto=0, cantidad_cuotas=1):
	monto_decimal = Decimal(str(monto or 0))
	if monto_decimal <= 0:
		raise ValueError("El monto a registrar en FerreCrédito debe ser mayor a 0.")

	try:
		cuotas = int(cantidad_cuotas)
	except (TypeError, ValueError) as exc:
		raise ValueError("La cantidad de cuotas no es válida.") from exc

	if cuotas < 1:
		raise ValueError("La cantidad de cuotas debe ser al menos 1.")

	movimiento_existente = None
	if pedido is not None:
		movimiento_existente = MovimientoCredito.objects.filter(
			cuenta=cuenta,
			tipo=MovimientoCredito.Tipo.COMPRA,
			pedido=pedido,
		).order_by("-creado_en").first()

	if movimiento_existente:
		return movimiento_existente

	descripcion_pedido = (
		f"Compra pedido #{pedido.pk} | cuotas={cuotas}"
		if pedido is not None
		else f"Compra FerreCrédito | cuotas={cuotas}"
	)

	movimiento = MovimientoCredito.objects.create(
		cuenta=cuenta,
		pedido=pedido,
		tipo=MovimientoCredito.Tipo.COMPRA,
		monto=monto_decimal,
		descripcion=descripcion_pedido,
	)

	cuenta.saldo_usado = Decimal(cuenta.saldo_usado) + monto_decimal
	cuenta.save(update_fields=["saldo_usado", "actualizado_en"])

	monto_base_cuota = (monto_decimal / Decimal(cuotas)).quantize(Decimal("0.01"))
	acumulado = Decimal("0.00")
	fecha_base = timezone.localdate()

	for numero in range(1, cuotas + 1):
		if numero < cuotas:
			monto_cuota = monto_base_cuota
		else:
			monto_cuota = monto_decimal - acumulado

		CuotaCredito.objects.create(
			cuenta=cuenta,
			pedido=pedido,
			numero_cuota=numero,
			total_cuotas=cuotas,
			monto=monto_cuota,
			fecha_vencimiento=_sumar_meses(fecha_base, numero),
			estado=CuotaCredito.Estado.PENDIENTE,
		)
		acumulado += monto_cuota

	return movimiento


@transaction.atomic
def marcar_cuota_pagada(cuota_id):
	cuota = CuotaCredito.objects.select_for_update().select_related("cuenta").filter(pk=cuota_id).first()
	if cuota is None:
		raise ValueError("La cuota seleccionada no existe.")

	if cuota.estado == CuotaCredito.Estado.PAGADA:
		return cuota

	cuota.estado = CuotaCredito.Estado.PAGADA
	cuota.save(update_fields=["estado"])

	cuenta = cuota.cuenta
	nuevo_saldo_usado = cuenta.saldo_usado - cuota.monto
	cuenta.saldo_usado = nuevo_saldo_usado if nuevo_saldo_usado > 0 else 0
	cuenta.save(update_fields=["saldo_usado"])
	return cuota


@transaction.atomic
def marcar_cuota_vencida(cuota_id):
	cuota = CuotaCredito.objects.select_for_update().filter(pk=cuota_id).first()
	if cuota is None:
		raise ValueError("La cuota seleccionada no existe.")

	if cuota.estado == CuotaCredito.Estado.PAGADA:
		raise ValueError("No puedes marcar vencida una cuota pagada.")

	if cuota.estado != CuotaCredito.Estado.VENCIDA:
		cuota.estado = CuotaCredito.Estado.VENCIDA
		cuota.save(update_fields=["estado"])

	return cuota


def obtener_datos_contador_credito(*, fecha_desde=None, fecha_hasta=None, estado_cuota=""):
	hoy = timezone.localdate()
	cuentas_qs = CuentaCredito.objects.select_related("maestro", "maestro__usuario")

	cuotas_qs = CuotaCredito.objects.select_related(
		"cuenta",
		"cuenta__maestro",
		"cuenta__maestro__usuario",
	)
	if estado_cuota:
		cuotas_qs = cuotas_qs.filter(estado=estado_cuota)

	if fecha_desde:
		cuotas_qs = cuotas_qs.filter(fecha_vencimiento__gte=fecha_desde)
	if fecha_hasta:
		cuotas_qs = cuotas_qs.filter(fecha_vencimiento__lte=fecha_hasta)

	total_credito_usado = cuentas_qs.aggregate(total=Sum("saldo_usado")).get("total") or 0
	total_cupo_aprobado = cuentas_qs.aggregate(total=Sum("cupo_aprobado")).get("total") or 0
	cuentas_credito_activas = cuentas_qs.filter(estado=CuentaCredito.Estado.ACTIVA).count()
	total_deuda_credito = cuotas_qs.aggregate(total=Sum("monto")).get("total") or 0

	cuotas_vencidas_qs = cuotas_qs.filter(
		Q(estado=CuotaCredito.Estado.VENCIDA)
		| Q(estado=CuotaCredito.Estado.PENDIENTE, fecha_vencimiento__lt=hoy)
	)

	return {
		"total_credito_usado": total_credito_usado,
		"total_cupo_aprobado": total_cupo_aprobado,
		"cuentas_credito_activas": cuentas_credito_activas,
		"total_deuda_credito": total_deuda_credito,
		"cuotas_vencidas": cuotas_vencidas_qs.count(),
		"monto_vencido": cuotas_vencidas_qs.aggregate(total=Sum("monto")).get("total") or 0,
		"cuotas_qs": cuotas_qs,
		"cuotas_recientes": list(cuotas_qs.order_by("-fecha_vencimiento", "-creado_en")[:10]),
	}


@transaction.atomic
def crear_solicitud_ferrecredito(usuario, datos):
	perfil = PerfilMaestroPyme.objects.filter(usuario=usuario).first()
	if not perfil:
		raise ValueError("Debes registrarte como Maestro/PYME para solicitar FerreCredito.")

	if perfil.estado != PerfilMaestroPyme.Estado.APROBADO:
		raise ValueError("Tu perfil Maestro/PYME debe estar aprobado para solicitar FerreCredito.")

	if SolicitudFerreCredito.objects.filter(
		maestro=perfil,
		estado=SolicitudFerreCredito.Estado.PENDIENTE,
	).exists():
		raise ValueError("Ya tienes una solicitud FerreCredito pendiente de revision.")

	try:
		monto_solicitado = Decimal(str(datos.get("monto_solicitado", "0")))
	except Exception as exc:
		raise ValueError("El monto solicitado no es valido.") from exc

	if monto_solicitado <= 0:
		raise ValueError("El monto solicitado debe ser mayor a 0.")

	motivo = (datos.get("motivo") or "").strip()

	return SolicitudFerreCredito.objects.create(
		maestro=perfil,
		monto_solicitado=monto_solicitado,
		motivo=motivo,
	)


@transaction.atomic
def aprobar_solicitud_ferrecredito(solicitud, cupo_aprobado, observacion_admin=""):
	if solicitud.estado != SolicitudFerreCredito.Estado.PENDIENTE:
		raise ValueError("Solo se pueden aprobar solicitudes en estado pendiente.")

	try:
		cupo = Decimal(str(cupo_aprobado))
	except Exception as exc:
		raise ValueError("El cupo aprobado no es valido.") from exc

	if cupo <= 0:
		raise ValueError("El cupo aprobado debe ser mayor a 0.")

	solicitud.estado = SolicitudFerreCredito.Estado.APROBADA
	solicitud.cupo_aprobado = cupo
	solicitud.observacion_admin = (observacion_admin or "").strip()
	solicitud.save(update_fields=["estado", "cupo_aprobado", "observacion_admin", "actualizado_en"])

	cuenta, creada = CuentaCredito.objects.get_or_create(
		maestro=solicitud.maestro,
		defaults={
			"cupo_aprobado": cupo,
			"estado": CuentaCredito.Estado.ACTIVA,
		},
	)

	if not creada:
		cuenta.cupo_aprobado = cupo
		cuenta.estado = CuentaCredito.Estado.ACTIVA
		cuenta.save(update_fields=["cupo_aprobado", "estado", "actualizado_en"])

	return solicitud, cuenta


@transaction.atomic
def rechazar_solicitud_ferrecredito(solicitud, observacion_admin=""):
	if solicitud.estado != SolicitudFerreCredito.Estado.PENDIENTE:
		raise ValueError("Solo se pueden rechazar solicitudes en estado pendiente.")

	solicitud.estado = SolicitudFerreCredito.Estado.RECHAZADA
	solicitud.observacion_admin = (observacion_admin or "").strip()
	solicitud.save(update_fields=["estado", "observacion_admin", "actualizado_en"])
	return solicitud


def obtener_resumen_admin_credito():
	solicitudes = SolicitudFerreCredito.objects.select_related("maestro__usuario").order_by("-creado_en")
	cuentas = CuentaCredito.objects.select_related("maestro__usuario").order_by("-creado_en")

	return {
		"total_solicitudes": solicitudes.count(),
		"total_pendientes": solicitudes.filter(estado=SolicitudFerreCredito.Estado.PENDIENTE).count(),
		"total_aprobadas": solicitudes.filter(estado=SolicitudFerreCredito.Estado.APROBADA).count(),
		"total_rechazadas": solicitudes.filter(estado=SolicitudFerreCredito.Estado.RECHAZADA).count(),
		"total_cuentas": cuentas.count(),
		"total_cupo_aprobado": cuentas.aggregate(total=Sum("cupo_aprobado"))["total"] or Decimal("0"),
		"total_saldo_usado": cuentas.aggregate(total=Sum("saldo_usado"))["total"] or Decimal("0"),
		"solicitudes_recientes": list(solicitudes[:30]),
		"cuentas": list(cuentas[:30]),
	}
