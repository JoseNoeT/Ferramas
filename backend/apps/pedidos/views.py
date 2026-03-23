from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from apps.pedidos import services as pedidos_services
from apps.pedidos.models import Pedido
from apps.usuarios.models import Usuario


def _requiere_rol(*roles):
    """Decorador que verifica que el usuario autenticado tenga uno de los roles indicados."""
    def decorador(view_func):
        @login_required
        def wrapper(request, *args, **kwargs):
            if request.user.rol not in roles:
                return HttpResponseForbidden(
                    "No tienes permiso para acceder a esta sección."
                )
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorador


@login_required
def carrito_view(request):
    resumen = pedidos_services.obtener_resumen_carrito(request.user)
    return render(request, "pages/carrito.html", resumen)


@login_required
def agregar_al_carrito_view(request):
    if request.method != "POST":
        return redirect("catalogo")
    producto_id = request.POST.get("producto_id")
    cantidad = request.POST.get("cantidad", 1)
    next_url = request.POST.get("next", "carrito")
    try:
        pedidos_services.agregar_producto_al_carrito(request.user, producto_id, cantidad)
        messages.success(request, "Producto agregado correctamente al carrito.")
    except ValueError as exc:
        messages.error(request, str(exc))
    return redirect(next_url)


@login_required
def actualizar_item_carrito_view(request):
    if request.method != "POST":
        return redirect("carrito")
    item_id = request.POST.get("item_id")
    cantidad = request.POST.get("cantidad", 1)
    try:
        pedidos_services.actualizar_cantidad_item(request.user, item_id, cantidad)
        messages.success(request, "Cantidad actualizada.")
    except ValueError as exc:
        messages.error(request, str(exc))
    return redirect("carrito")


@login_required
def eliminar_item_carrito_view(request):
    if request.method != "POST":
        return redirect("carrito")
    item_id = request.POST.get("item_id")
    pedidos_services.eliminar_item_del_carrito(request.user, item_id)
    messages.success(request, "Producto eliminado del carrito.")
    return redirect("carrito")


@login_required
def checkout_view(request):
    resumen = pedidos_services.obtener_resumen_carrito(request.user)
    if request.method == "POST":
        tipo_entrega = request.POST.get("tipo_entrega", Pedido.TipoEntrega.RETIRO)
        try:
            pedido = pedidos_services.crear_pedido_desde_carrito(request.user, tipo_entrega)
            messages.success(request, f"Pedido #{pedido.pk} generado correctamente.")
            return redirect("confirmacion", pk=pedido.pk)
        except ValueError as exc:
            messages.error(request, str(exc))
    return render(request, "pages/checkout.html", resumen)


@login_required
def pedido_confirmacion_view(request, pk):
    try:
        pedido = (
            Pedido.objects.prefetch_related("items__producto")
            .get(pk=pk, usuario=request.user)
        )
    except Pedido.DoesNotExist:
        raise Http404("Pedido no encontrado.")
    return render(request, "pages/confirmacion.html", {"pedido": pedido})


# ─── Dashboard Vendedor ───────────────────────────────────────────────────────

@_requiere_rol(Usuario.Rol.VENDEDOR, Usuario.Rol.ADMIN)
def vendedor_dashboard_view(request):
    pedidos = (
        Pedido.objects
        .select_related("usuario")
        .filter(estado=Pedido.Estado.GENERADO)
        .order_by("-creado_en")
    )
    return render(request, "dashboard/vendedor.html", {"pedidos": pedidos})


@_requiere_rol(Usuario.Rol.VENDEDOR, Usuario.Rol.ADMIN)
def aprobar_pedido_view(request, pk):
    if request.method != "POST":
        return redirect("vendedor_dashboard")
    pedido = get_object_or_404(Pedido, pk=pk)
    try:
        pedidos_services.aprobar_pedido(pedido)
        messages.success(request, f"Pedido #{pedido.pk} aprobado correctamente.")
    except ValueError as exc:
        messages.error(request, str(exc))
    return redirect("vendedor_dashboard")


@_requiere_rol(Usuario.Rol.VENDEDOR, Usuario.Rol.ADMIN)
def rechazar_pedido_view(request, pk):
    if request.method != "POST":
        return redirect("vendedor_dashboard")
    pedido = get_object_or_404(Pedido, pk=pk)
    try:
        pedidos_services.rechazar_pedido(pedido)
        messages.warning(request, f"Pedido #{pedido.pk} rechazado.")
    except ValueError as exc:
        messages.error(request, str(exc))
    return redirect("vendedor_dashboard")


# ─── Dashboard Bodeguero ──────────────────────────────────────────────────────

@_requiere_rol(Usuario.Rol.BODEGUERO, Usuario.Rol.ADMIN)
def bodeguero_dashboard_view(request):
    pedidos = (
        Pedido.objects
        .select_related("usuario")
        .filter(estado__in=[Pedido.Estado.APROBADO, Pedido.Estado.EN_PREPARACION])
        .order_by("-creado_en")
    )
    return render(request, "dashboard/bodeguero.html", {"pedidos": pedidos})


@_requiere_rol(Usuario.Rol.BODEGUERO, Usuario.Rol.ADMIN)
def poner_en_preparacion_view(request, pk):
    if request.method != "POST":
        return redirect("bodeguero_dashboard")
    pedido = get_object_or_404(Pedido, pk=pk)
    try:
        pedidos_services.poner_en_preparacion(pedido)
        messages.success(request, f"Pedido #{pedido.pk} en preparación.")
    except ValueError as exc:
        messages.error(request, str(exc))
    return redirect("bodeguero_dashboard")


@_requiere_rol(Usuario.Rol.BODEGUERO, Usuario.Rol.ADMIN)
def marcar_pedido_listo_view(request, pk):
    if request.method != "POST":
        return redirect("bodeguero_dashboard")
    pedido = get_object_or_404(Pedido, pk=pk)
    try:
        pedidos_services.marcar_pedido_listo(pedido)
        messages.success(request, f"Pedido #{pedido.pk} marcado como listo.")
    except ValueError as exc:
        messages.error(request, str(exc))
    return redirect("bodeguero_dashboard")
