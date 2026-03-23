from apps.pedidos.models import ItemCarrito


def carrito_context(request):
    """Expone el total de unidades del carrito para el navbar."""
    if not getattr(request, "user", None) or not request.user.is_authenticated:
        return {"carrito_items_total": 0}

    total = (
        ItemCarrito.objects.filter(carrito__usuario=request.user)
        .values_list("cantidad", flat=True)
    )
    return {"carrito_items_total": sum(total)}