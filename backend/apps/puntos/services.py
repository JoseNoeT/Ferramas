from decimal import Decimal, ROUND_DOWN

from django.db import transaction

from apps.puntos.models import CuentaPuntos, MovimientoPuntos


def obtener_o_crear_cuenta_puntos(usuario):
	cuenta, _ = CuentaPuntos.objects.get_or_create(usuario=usuario)
	return cuenta


def calcular_puntos_ganados(monto_pagado):
	monto_decimal = Decimal(monto_pagado or 0)
	if monto_decimal <= 0:
		return 0
	return int((monto_decimal / Decimal("100")).to_integral_value(rounding=ROUND_DOWN))


@transaction.atomic
def aplicar_puntos(usuario, pedido, puntos_a_usar):
	puntos_a_usar = int(puntos_a_usar or 0)
	if puntos_a_usar <= 0:
		return pedido

	cuenta = CuentaPuntos.objects.select_for_update().filter(usuario=usuario).first()
	if cuenta is None:
		cuenta = obtener_o_crear_cuenta_puntos(usuario)
		cuenta = CuentaPuntos.objects.select_for_update().get(pk=cuenta.pk)
	if puntos_a_usar > cuenta.saldo:
		raise ValueError("No tienes saldo de puntos suficiente.")

	total_pedido = Decimal(pedido.total or 0)
	if Decimal(puntos_a_usar) > total_pedido:
		raise ValueError("No puedes usar más puntos que el total del pedido.")

	cuenta.saldo -= puntos_a_usar
	cuenta.save(update_fields=["saldo", "actualizado_en"])

	descuento = Decimal(puntos_a_usar)
	pedido.puntos_usados = puntos_a_usar
	pedido.descuento_puntos = descuento
	pedido.total_final = total_pedido - descuento
	pedido.save(update_fields=["puntos_usados", "descuento_puntos", "total_final"])

	MovimientoPuntos.objects.create(
		cuenta=cuenta,
		pedido=pedido,
		tipo=MovimientoPuntos.Tipo.USADO,
		puntos=puntos_a_usar,
		saldo_resultante=cuenta.saldo,
		descripcion=f"Canje de puntos en pedido #{pedido.pk}",
	)
	return pedido


@transaction.atomic
def acumular_puntos_por_pedido(usuario, pedido):
	if MovimientoPuntos.objects.filter(
		cuenta__usuario=usuario,
		pedido=pedido,
		tipo=MovimientoPuntos.Tipo.GANADO,
	).exists():
		return 0

	puntos_ganados = calcular_puntos_ganados(pedido.total_final)
	if puntos_ganados <= 0:
		return 0

	cuenta = CuentaPuntos.objects.select_for_update().filter(usuario=usuario).first()
	if cuenta is None:
		cuenta = obtener_o_crear_cuenta_puntos(usuario)
		cuenta = CuentaPuntos.objects.select_for_update().get(pk=cuenta.pk)
	cuenta.saldo += puntos_ganados
	cuenta.save(update_fields=["saldo", "actualizado_en"])

	MovimientoPuntos.objects.create(
		cuenta=cuenta,
		pedido=pedido,
		tipo=MovimientoPuntos.Tipo.GANADO,
		puntos=puntos_ganados,
		saldo_resultante=cuenta.saldo,
		descripcion=f"Acumulación por pedido #{pedido.pk}",
	)
	return puntos_ganados


def obtener_resumen_puntos(usuario):
	cuenta = obtener_o_crear_cuenta_puntos(usuario)
	movimientos = list(cuenta.movimientos.select_related("pedido").all())

	total_ganados = sum(
		mov.puntos for mov in movimientos if mov.tipo == MovimientoPuntos.Tipo.GANADO
	)
	total_usados = sum(
		mov.puntos for mov in movimientos if mov.tipo == MovimientoPuntos.Tipo.USADO
	)

	return {
		"cuenta": cuenta,
		"saldo": cuenta.saldo,
		"total_ganados": total_ganados,
		"total_usados": total_usados,
		"movimientos": movimientos,
	}
