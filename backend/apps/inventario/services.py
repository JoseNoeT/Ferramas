from django.db import transaction

from apps.inventario.models import MovimientoInventario


def _items_producto_pedido(pedido):
	# Nota tecnica: se evita importar ItemPedido para reducir acoplamiento entre apps.
	# Se filtra por el valor persistido de tipo_linea en base de datos.
	return list(
		pedido.items.select_related("producto").filter(tipo_linea="producto")
	)


def registrar_movimiento_inventario(
	*,
	producto,
	pedido=None,
	tipo_movimiento,
	cantidad,
	stock_anterior,
	stock_nuevo,
	usuario=None,
	motivo="",
):
	return MovimientoInventario.objects.create(
		producto=producto,
		pedido=pedido,
		tipo_movimiento=tipo_movimiento,
		cantidad=int(cantidad),
		stock_anterior=int(stock_anterior),
		stock_nuevo=int(stock_nuevo),
		usuario=usuario,
		motivo=motivo,
	)


@transaction.atomic
def validar_stock_pedido(pedido):
	items = _items_producto_pedido(pedido)
	for item in items:
		producto = item.producto.__class__.objects.select_for_update().get(pk=item.producto_id)
		if item.cantidad > producto.stock:
			raise ValueError(
				f"Stock insuficiente para '{producto.nombre}'. Disponible: {producto.stock}."
			)
	return True


@transaction.atomic
def reservar_stock_pedido(pedido, usuario=None):
	if pedido.stock_reservado:
		return pedido

	if pedido.stock_descontado:
		raise ValueError("El pedido ya tiene stock descontado; no se puede reservar nuevamente.")

	validar_stock_pedido(pedido)
	items = _items_producto_pedido(pedido)
	for item in items:
		producto = item.producto.__class__.objects.select_for_update().get(pk=item.producto_id)
		stock_anterior = producto.stock
		producto.stock = stock_anterior - item.cantidad
		producto.save(update_fields=["stock"])
		registrar_movimiento_inventario(
			producto=producto,
			pedido=pedido,
			tipo_movimiento=MovimientoInventario.TipoMovimiento.RESERVA,
			cantidad=item.cantidad,
			stock_anterior=stock_anterior,
			stock_nuevo=producto.stock,
			usuario=usuario,
			motivo="Reserva de stock al generar pedido.",
		)

	pedido.stock_reservado = True
	pedido.save(update_fields=["stock_reservado"])
	return pedido


@transaction.atomic
def descontar_stock_pedido(pedido, usuario=None):
	if pedido.stock_descontado:
		return pedido

	if pedido.stock_reservado:
		# El stock ya fue descontado físicamente al reservar.
		pedido.stock_descontado = True
		pedido.save(update_fields=["stock_descontado"])
		for item in _items_producto_pedido(pedido):
			producto = item.producto
			registrar_movimiento_inventario(
				producto=producto,
				pedido=pedido,
				tipo_movimiento=MovimientoInventario.TipoMovimiento.AJUSTE,
				cantidad=0,
				stock_anterior=producto.stock,
				stock_nuevo=producto.stock,
				usuario=usuario,
				motivo="Confirmacion de descuento sobre stock previamente reservado.",
			)
		return pedido

	validar_stock_pedido(pedido)
	for item in _items_producto_pedido(pedido):
		producto = item.producto.__class__.objects.select_for_update().get(pk=item.producto_id)
		stock_anterior = producto.stock
		producto.stock = stock_anterior - item.cantidad
		producto.save(update_fields=["stock"])
		registrar_movimiento_inventario(
			producto=producto,
			pedido=pedido,
			tipo_movimiento=MovimientoInventario.TipoMovimiento.SALIDA,
			cantidad=item.cantidad,
			stock_anterior=stock_anterior,
			stock_nuevo=producto.stock,
			usuario=usuario,
			motivo="Descuento de stock por pedido.",
		)

	pedido.stock_descontado = True
	pedido.save(update_fields=["stock_descontado"])
	return pedido


@transaction.atomic
def liberar_stock_pedido(pedido, usuario=None):
	if not pedido.stock_reservado and not pedido.stock_descontado:
		return pedido

	for item in _items_producto_pedido(pedido):
		producto = item.producto.__class__.objects.select_for_update().get(pk=item.producto_id)
		stock_anterior = producto.stock
		producto.stock = stock_anterior + item.cantidad
		producto.save(update_fields=["stock"])
		registrar_movimiento_inventario(
			producto=producto,
			pedido=pedido,
			tipo_movimiento=MovimientoInventario.TipoMovimiento.LIBERACION,
			cantidad=item.cantidad,
			stock_anterior=stock_anterior,
			stock_nuevo=producto.stock,
			usuario=usuario,
			motivo="Liberacion de stock por rechazo/cancelacion de pedido.",
		)

	pedido.stock_reservado = False
	pedido.stock_descontado = False
	pedido.save(update_fields=["stock_reservado", "stock_descontado"])
	return pedido


@transaction.atomic
def registrar_inicio_preparacion_pedido(pedido, usuario=None):
	for item in _items_producto_pedido(pedido):
		producto = item.producto
		registrar_movimiento_inventario(
			producto=producto,
			pedido=pedido,
			tipo_movimiento=MovimientoInventario.TipoMovimiento.AJUSTE,
			cantidad=0,
			stock_anterior=producto.stock,
			stock_nuevo=producto.stock,
			usuario=usuario,
			motivo="Inicio de preparacion en bodega.",
		)
	return pedido


@transaction.atomic
def registrar_pedido_listo(pedido, usuario=None):
	for item in _items_producto_pedido(pedido):
		producto = item.producto
		registrar_movimiento_inventario(
			producto=producto,
			pedido=pedido,
			tipo_movimiento=MovimientoInventario.TipoMovimiento.AJUSTE,
			cantidad=0,
			stock_anterior=producto.stock,
			stock_nuevo=producto.stock,
			usuario=usuario,
			motivo="Pedido marcado como listo en bodega.",
		)
	return pedido
