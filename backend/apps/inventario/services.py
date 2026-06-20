from django.db import transaction

from apps.inventario.models import MovimientoInventario
from apps.catalogo.models import Producto, Categoria


def obtener_productos_stock_bodega(categoria_id=None, estado=None, busqueda=None):
	"""Retorna lista de productos con stock y estado.

	Cada elemento es dict: {producto, categoria, stock, stock_minimo, estado}
	Estado: 'OK', 'Bajo stock', 'Sin stock'
	Soporta filtros por categoria_id, estado y busqueda (nombre).
	"""
	qs = Producto.objects.select_related("categoria").filter(activo=True)
	if categoria_id:
		qs = qs.filter(categoria_id=categoria_id)
	if busqueda:
		qs = qs.filter(nombre__icontains=busqueda)

	resultado = []
	for p in qs.order_by("nombre"):
		stock_minimo = getattr(p, "stock_minimo", None)
		if p.stock == 0:
			estado_val = "Sin stock"
		elif stock_minimo is not None and p.stock <= stock_minimo:
			estado_val = "Bajo stock"
		else:
			estado_val = "OK"
		resultado.append(
			{
				"producto": p,
				"categoria": p.categoria,
				"stock": p.stock,
				"stock_minimo": stock_minimo,
				"estado": estado_val,
			}
		)

	if estado:
		estado_map = {"ok": "OK", "bajo_stock": "Bajo stock", "sin_stock": "Sin stock"}
		expected = estado_map.get(estado)
		if expected:
			resultado = [r for r in resultado if r["estado"] == expected]

	return resultado


def obtener_productos_bajo_stock():
	"""Retorna lista de productos con stock bajo o sin stock."""
	productos = Producto.objects.select_related("categoria").filter(activo=True)
	bajos = []
	for p in productos:
		stock_minimo = getattr(p, "stock_minimo", None)
		if p.stock == 0 or (stock_minimo is not None and p.stock <= stock_minimo):
			bajos.append({"producto": p, "stock": p.stock, "stock_minimo": stock_minimo})
	return bajos


def obtener_ultimos_movimientos(limit=10):
	return MovimientoInventario.objects.select_related("producto", "usuario").all()[:limit]


@transaction.atomic
def ajustar_stock_producto(producto_id, cantidad, tipo_movimiento, motivo, usuario=None):
	"""Ajusta el stock de un producto y registra MovimientoInventario.

	- `cantidad` debe ser entero positivo.
	- Para SALIDA se restará, para ENTRADA se sumará, para AJUSTE se aplica como delta.
	- No permite stock negativo.
	"""
	cantidad = int(cantidad)
	if cantidad < 0:
		raise ValueError("La cantidad debe ser un entero positivo.")

	producto = Producto.objects.select_for_update().get(pk=producto_id)
	stock_anterior = producto.stock

	if tipo_movimiento == MovimientoInventario.TipoMovimiento.ENTRADA:
		stock_nuevo = stock_anterior + cantidad
	elif tipo_movimiento == MovimientoInventario.TipoMovimiento.SALIDA:
		if cantidad > stock_anterior:
			raise ValueError("Salida supera el stock disponible; operación no permitida.")
		stock_nuevo = stock_anterior - cantidad
	elif tipo_movimiento == MovimientoInventario.TipoMovimiento.AJUSTE:
		stock_nuevo = stock_anterior + cantidad
		if stock_nuevo < 0:
			raise ValueError("El ajuste produciría stock negativo; operación no permitida.")
	else:
		raise ValueError("Tipo de movimiento inválido para ajuste manual.")

	producto.stock = stock_nuevo
	producto.save(update_fields=["stock"])

	registrar_movimiento_inventario(
		producto=producto,
		pedido=None,
		tipo_movimiento=tipo_movimiento,
		cantidad=cantidad,
		stock_anterior=stock_anterior,
		stock_nuevo=stock_nuevo,
		usuario=usuario,
		motivo=motivo or "Ajuste manual en bodega",
	)

	return producto


def obtener_resumen_stock_bodega():
	total = Producto.objects.filter(activo=True).count()
	sin_stock = Producto.objects.filter(activo=True, stock=0).count()
	bajos = 0
	for p in Producto.objects.filter(activo=True):
		if getattr(p, "stock_minimo", None) is not None and p.stock <= p.stock_minimo:
			bajos += 1
	# Devolver claves compatibles con plantilla antigua y nuevas claves explícitas
	return {
		"total": total,
		"sin_stock": sin_stock,
		"bajo_stock": bajos,
		"total_productos": total,
		"productos_sin_stock": sin_stock,
		"productos_bajo_stock": bajos,
	}


def obtener_productos_sin_stock():
	"""Retorna lista de productos con stock == 0."""
	productos = Producto.objects.select_related("categoria").filter(activo=True, stock=0)
	resultado = []
	for p in productos.order_by("nombre"):
		resultado.append({"producto": p, "stock": p.stock, "stock_minimo": getattr(p, "stock_minimo", None)})
	return resultado


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
