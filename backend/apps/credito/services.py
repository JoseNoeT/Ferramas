from datetime import date
from decimal import Decimal

from django.db import transaction
from django.db.models import Sum
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
def registrar_compra_ferrecredito(cuenta, pedido, monto, cantidad_cuotas):
	monto_decimal = Decimal(str(monto or 0))
	if monto_decimal <= 0:
		raise ValueError("El monto a registrar en FerreCrédito debe ser mayor a 0.")

	try:
		cuotas = int(cantidad_cuotas)
	except (TypeError, ValueError) as exc:
		raise ValueError("La cantidad de cuotas no es válida.") from exc

	if cuotas < 1:
		raise ValueError("La cantidad de cuotas debe ser al menos 1.")

	descripcion_pedido = f"Compra pedido #{pedido.pk} | cuotas={cuotas}"
	if MovimientoCredito.objects.filter(
		cuenta=cuenta,
		tipo=MovimientoCredito.Tipo.COMPRA,
		descripcion=descripcion_pedido,
	).exists():
		raise ValueError("La compra con FerreCrédito para este pedido ya fue registrada.")

	movimiento = MovimientoCredito.objects.create(
		cuenta=cuenta,
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
			numero_cuota=numero,
			total_cuotas=cuotas,
			monto=monto_cuota,
			fecha_vencimiento=_sumar_meses(fecha_base, numero),
			estado=CuotaCredito.Estado.PENDIENTE,
		)
		acumulado += monto_cuota

	return movimiento


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
