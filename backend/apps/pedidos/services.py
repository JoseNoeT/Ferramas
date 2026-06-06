from django.db import transaction

from apps.catalogo.services import obtener_precio_efectivo
from apps.catalogo.models import Producto
from apps.inventario import services as inventario_services
from apps.pedidos.models import Carrito, ItemCarrito, ItemPedido, Pedido


def _recalcular_totales_pedido(pedido):
    subtotal = sum(item.subtotal for item in pedido.items.all())
    pedido.subtotal = subtotal
    pedido.total = subtotal
    if pedido.puntos_usados == 0:
        pedido.total_final = subtotal
        pedido.save(update_fields=["subtotal", "total", "total_final"])
    else:
        pedido.save(update_fields=["subtotal", "total"])
    return pedido


def obtener_o_crear_carrito(usuario):
    """Retorna el carrito del usuario, creandolo si no existe."""
    carrito, _ = Carrito.objects.get_or_create(usuario=usuario)
    return carrito


def agregar_producto_al_carrito(usuario, producto_id, cantidad):
    """Agrega un producto al carrito. Si ya existe, suma la cantidad."""
    cantidad = int(cantidad)
    if cantidad < 1:
        raise ValueError("La cantidad debe ser al menos 1.")

    try:
        producto = Producto.objects.get(pk=producto_id, activo=True)
    except Producto.DoesNotExist:
        raise ValueError("Producto no encontrado.")

    carrito = obtener_o_crear_carrito(usuario)
    item, _ = ItemCarrito.objects.get_or_create(
        carrito=carrito, producto=producto, defaults={"cantidad": 0}
    )
    nueva_cantidad = item.cantidad + cantidad
    if nueva_cantidad > producto.stock:
        raise ValueError(f"Stock insuficiente. Disponible: {producto.stock}.")
    item.cantidad = nueva_cantidad
    item.save()
    return item


def actualizar_cantidad_item(usuario, item_id, cantidad):
    """Actualiza la cantidad de un item del carrito."""
    cantidad = int(cantidad)
    if cantidad < 1:
        raise ValueError("La cantidad minima es 1.")

    carrito = obtener_o_crear_carrito(usuario)
    try:
        item = ItemCarrito.objects.select_related("producto").get(
            pk=item_id, carrito=carrito
        )
    except ItemCarrito.DoesNotExist:
        raise ValueError("Item no encontrado en el carrito.")

    if cantidad > item.producto.stock:
        raise ValueError(f"Stock insuficiente. Disponible: {item.producto.stock}.")
    item.cantidad = cantidad
    item.save()
    return item


def eliminar_item_del_carrito(usuario, item_id):
    """Elimina un item del carrito del usuario."""
    carrito = obtener_o_crear_carrito(usuario)
    ItemCarrito.objects.filter(pk=item_id, carrito=carrito).delete()


def obtener_resumen_carrito(usuario):
    """Retorna items, subtotal y total del carrito del usuario."""
    carrito = obtener_o_crear_carrito(usuario)
    items = list(carrito.items.select_related("producto").all())
    subtotal = sum(item.subtotal for item in items)
    return {
        "carrito": carrito,
        "items": items,
        "subtotal": subtotal,
        "total": subtotal,
    }


# ─── Transiciones internas de flujo ─────────────────────────────────────────

def aprobar_pedido(pedido, usuario=None):
    """Aprueba un pedido generado. Solo válido desde estado 'generado'."""
    if pedido.estado != Pedido.Estado.GENERADO:
        raise ValueError("Solo se pueden aprobar pedidos en estado 'generado'.")
    pedido.estado = Pedido.Estado.APROBADO
    pedido.save(update_fields=["estado"])
    return pedido


@transaction.atomic
def rechazar_pedido(pedido, usuario=None):
    """Rechaza un pedido generado. Solo válido desde estado 'generado'."""
    if pedido.estado != Pedido.Estado.GENERADO:
        raise ValueError("Solo se pueden rechazar pedidos en estado 'generado'.")

    inventario_services.liberar_stock_pedido(pedido, usuario=usuario)
    pedido.estado = Pedido.Estado.RECHAZADO
    pedido.save(update_fields=["estado"])
    return pedido


@transaction.atomic
def poner_en_preparacion(pedido, usuario=None):
    """Pasa un pedido aprobado a en preparación. Solo válido desde 'aprobado'."""
    if pedido.estado != Pedido.Estado.APROBADO:
        raise ValueError("Solo se pueden preparar pedidos en estado 'aprobado'.")

    if not pedido.stock_reservado and not pedido.stock_descontado:
        inventario_services.reservar_stock_pedido(
            pedido,
            usuario=usuario,
        )

    inventario_services.registrar_inicio_preparacion_pedido(
        pedido,
        usuario=usuario,
    )

    pedido.estado = Pedido.Estado.EN_PREPARACION
    pedido.save(update_fields=["estado"])
    return pedido


@transaction.atomic
def marcar_pedido_listo(pedido, usuario=None):
    """Marca un pedido en preparación como listo. Solo válido desde 'en_preparacion'."""
    if pedido.estado != Pedido.Estado.EN_PREPARACION:
        raise ValueError("Solo se pueden marcar como listos pedidos en estado 'en_preparacion'.")

    inventario_services.registrar_pedido_listo(
        pedido,
        usuario=usuario,
    )

    pedido.estado = Pedido.Estado.LISTO
    pedido.save(update_fields=["estado"])
    return pedido


# ─── Creación de pedido desde carrito ────────────────────────────────────────

@transaction.atomic
def crear_pedido_desde_carrito(usuario, tipo_entrega):
    """Convierte el carrito en un Pedido generado y limpia el carrito."""
    carrito = obtener_o_crear_carrito(usuario)
    items = list(carrito.items.select_related("producto").all())
    if not items:
        raise ValueError("El carrito esta vacio.")

    subtotal = sum(item.subtotal for item in items)
    pedido = Pedido.objects.create(
        usuario=usuario,
        estado=Pedido.Estado.GENERADO,
        tipo_entrega=tipo_entrega,
        subtotal=subtotal,
        total=subtotal,
        total_final=subtotal,
    )
    for item in items:
        ItemPedido.objects.create(
            pedido=pedido,
            tipo_linea=ItemPedido.TipoLinea.PRODUCTO,
            producto=item.producto,
            cantidad=item.cantidad,
            precio_unitario=obtener_precio_efectivo(item.producto),
        )

    inventario_services.validar_stock_pedido(pedido)
    inventario_services.reservar_stock_pedido(pedido, usuario=usuario)

    carrito.items.all().delete()
    return pedido


@transaction.atomic
def agregar_asesoria_a_pedido(pedido, solicitud_asesoria):
    ItemPedido.objects.create(
        pedido=pedido,
        tipo_linea=ItemPedido.TipoLinea.ASESORIA,
        solicitud_asesoria=solicitud_asesoria,
        descripcion=f"Confirmacion asesoria Maestro/PYME: {solicitud_asesoria.servicio.titulo}",
        cantidad=1,
        precio_unitario=solicitud_asesoria.cargo_confirmacion,
    )
    _recalcular_totales_pedido(pedido)
    return pedido
