from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.catalogo.models import Producto
from apps.pedidos import services as pedidos_services
from apps.pedidos.models import Pedido
from apps.pedidos.serializers import (
    AgregarCarritoSerializer,
    CrearPedidoSerializer,
    EliminarCarritoSerializer,
    ItemCarritoSerializer,
    PedidoSerializer,
    ResumenCarritoSerializer,
)
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
    pedidos_pendientes = (
        Pedido.objects
        .select_related("usuario")
        .filter(estado=Pedido.Estado.GENERADO)
        .order_by("-creado_en")
    )
    pedidos_aprobados = (
        Pedido.objects
        .select_related("usuario")
        .filter(estado=Pedido.Estado.APROBADO)
        .order_by("-creado_en")
    )
    productos_bodega = (
        Producto.objects
        .select_related("categoria")
        .filter(activo=True, stock__gt=0)
        .order_by("nombre")
    )
    return render(request, "dashboard/vendedor.html", {
        "pedidos": pedidos_pendientes,
        "pedidos_aprobados": pedidos_aprobados,
        "productos_bodega": productos_bodega,
    })


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


@_requiere_rol(Usuario.Rol.VENDEDOR, Usuario.Rol.ADMIN)
def enviar_a_bodega_view(request, pk):
    """Envía un pedido aprobado a bodega (pasa a en_preparacion)."""
    if request.method != "POST":
        return redirect("vendedor_dashboard")
    pedido = get_object_or_404(Pedido, pk=pk)
    try:
        pedidos_services.poner_en_preparacion(pedido)
        messages.success(request, f"Pedido #{pedido.pk} enviado a bodega para preparación.")
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


def _es_prefijo_api(request, prefijo):
    return request.path.startswith(prefijo)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def api_carrito_o_pedidos_root_view(request):
    """Despacha GET de /api/carrito/ y /api/pedidos/ según prefijo."""
    if _es_prefijo_api(request, "/api/carrito/"):
        resumen = pedidos_services.obtener_resumen_carrito(request.user)
        serializer = ResumenCarritoSerializer(resumen)
        return Response(serializer.data, status=status.HTTP_200_OK)

    if _es_prefijo_api(request, "/api/pedidos/"):
        pedidos = (
            Pedido.objects.filter(usuario=request.user)
            .prefetch_related("items__producto")
            .order_by("-creado_en")
        )
        serializer = PedidoSerializer(pedidos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response({"detail": "Ruta no encontrada."}, status=status.HTTP_404_NOT_FOUND)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def api_carrito_agregar_view(request):
    """Agrega un producto al carrito del usuario autenticado."""
    if not _es_prefijo_api(request, "/api/carrito/"):
        return Response({"detail": "Ruta no encontrada."}, status=status.HTTP_404_NOT_FOUND)

    serializer = AgregarCarritoSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        item = pedidos_services.agregar_producto_al_carrito(
            request.user,
            serializer.validated_data["producto_id"],
            serializer.validated_data["cantidad"],
        )
    except ValueError as exc:
        return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    response_serializer = ItemCarritoSerializer(item)
    return Response(response_serializer.data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def api_carrito_eliminar_view(request):
    """Elimina un item del carrito del usuario autenticado."""
    if not _es_prefijo_api(request, "/api/carrito/"):
        return Response({"detail": "Ruta no encontrada."}, status=status.HTTP_404_NOT_FOUND)

    serializer = EliminarCarritoSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    pedidos_services.eliminar_item_del_carrito(request.user, serializer.validated_data["item_id"])
    return Response({"detail": "Item eliminado."}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def api_pedidos_create_view(request):
    """Crea un pedido desde el carrito actual."""
    if not _es_prefijo_api(request, "/api/pedidos/"):
        return Response({"detail": "Ruta no encontrada."}, status=status.HTTP_404_NOT_FOUND)

    serializer = CrearPedidoSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        pedido = pedidos_services.crear_pedido_desde_carrito(
            request.user,
            serializer.validated_data["tipo_entrega"],
        )
    except ValueError as exc:
        return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    response_serializer = PedidoSerializer(pedido)
    return Response(response_serializer.data, status=status.HTTP_201_CREATED)
