from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
import re
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.credito import services as credito_services
from apps.credito.models import MovimientoCredito
from apps.catalogo.models import Producto
from apps.maestros.models import PerfilMaestroPyme, SolicitudAsesoria
from apps.pagos.models import Pago
from apps.pagos import services as pagos_services
from apps.pedidos import services as pedidos_services
from apps.inventario import services as inventario_services
from apps.catalogo.models import Categoria
from apps.pedidos.models import Pedido
from apps.puntos import services as puntos_services
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
    def obtener_solicitud_pendiente_desde_session():
        solicitud_id = request.session.get("solicitud_asesoria_pendiente_id")
        if not solicitud_id:
            return None

        solicitud = (
            SolicitudAsesoria.objects.select_related("servicio__maestro")
            .filter(
                pk=solicitud_id,
                cliente=request.user,
                servicio__activo=True,
                servicio__maestro__estado=PerfilMaestroPyme.Estado.APROBADO,
            )
            .first()
        )
        if not solicitud:
            request.session.pop("solicitud_asesoria_pendiente_id", None)
            request.session.modified = True
            return None
        return solicitud

    cuenta_puntos = puntos_services.obtener_o_crear_cuenta_puntos(request.user)
    resumen = pedidos_services.obtener_resumen_carrito(request.user)
    solicitud_pendiente = obtener_solicitud_pendiente_desde_session()
    perfil_maestro = PerfilMaestroPyme.objects.filter(usuario=request.user).first()
    cargo_asesoria_pendiente = solicitud_pendiente.cargo_confirmacion if solicitud_pendiente else 0
    total_con_asesoria = resumen["total"] + cargo_asesoria_pendiente

    resumen["solicitud_asesoria_pendiente"] = solicitud_pendiente
    resumen["cargo_asesoria_pendiente"] = cargo_asesoria_pendiente
    resumen["total_con_asesoria"] = total_con_asesoria
    resumen["saldo_puntos"] = cuenta_puntos.saldo
    resumen["es_maestro_aprobado"] = (
        perfil_maestro is not None and perfil_maestro.estado == PerfilMaestroPyme.Estado.APROBADO
    )

    cuenta_credito = credito_services.obtener_cuenta_credito_usuario(request.user)
    cuotas_vencidas_credito = False
    saldo_disponible_credito = 0
    puede_usar_ferrecredito = False

    if cuenta_credito:
        cuotas_vencidas_credito = credito_services.tiene_cuotas_vencidas(cuenta_credito)
        saldo_disponible_credito = cuenta_credito.saldo_disponible
        puede_usar_ferrecredito = (
            not cuotas_vencidas_credito and saldo_disponible_credito >= total_con_asesoria
        )

    resumen["cuenta_credito"] = cuenta_credito
    resumen["puede_usar_ferrecredito"] = puede_usar_ferrecredito
    resumen["saldo_disponible_credito"] = saldo_disponible_credito
    resumen["tiene_cuotas_vencidas"] = cuotas_vencidas_credito

    if request.method == "POST":
        tipo_entrega = request.POST.get("tipo_entrega", Pedido.TipoEntrega.RETIRO)
        puntos_a_usar = request.POST.get("puntos_a_usar", 0)
        medio_pago = request.POST.get("medio_pago", "tienda")
        cantidad_cuotas = request.POST.get("cantidad_cuotas", 1)
        try:
            with transaction.atomic():
                pedido = pedidos_services.crear_pedido_desde_carrito(request.user, tipo_entrega)

                solicitud_pendiente_post = obtener_solicitud_pendiente_desde_session()
                if solicitud_pendiente_post:
                    pedidos_services.agregar_asesoria_a_pedido(pedido, solicitud_pendiente_post)
                    request.session.pop("solicitud_asesoria_pendiente_id", None)
                    request.session.modified = True

                if int(puntos_a_usar or 0) > 0:
                    puntos_services.aplicar_puntos(request.user, pedido, puntos_a_usar)
                else:
                    pedido.total_final = pedido.total
                    pedido.save(update_fields=["total_final"])

                if medio_pago == "ferrecredito":
                    cuenta_credito_post = credito_services.validar_uso_ferrecredito(
                        request.user,
                        pedido.total_final,
                    )
                    movimiento_credito = credito_services.registrar_compra_ferrecredito(
                        cuenta_credito_post,
                        pedido=pedido,
                        monto=pedido.total_final,
                        cantidad_cuotas=cantidad_cuotas,
                    )
                    pagos_services.registrar_pago_ferrecredito(
                        pedido,
                        movimiento_credito=movimiento_credito,
                        usuario=request.user,
                    )

                if medio_pago == "tienda":
                    pagos_services.registrar_pago_pendiente_tienda(
                        pedido,
                        usuario=request.user,
                    )

                if medio_pago != "webpay":
                    puntos_services.acumular_puntos_por_pedido(request.user, pedido)

            if medio_pago == "webpay":
                messages.info(request, "Redirigiendo a Webpay Plus para confirmar el pago.")
                return redirect("pagos:webpay_iniciar", pedido_id=pedido.pk)

            messages.success(request, f"Pedido #{pedido.pk} generado correctamente.")
            return redirect("confirmacion", pk=pedido.pk)
        except ValueError as exc:
            messages.error(request, str(exc))
    return render(request, "pages/checkout.html", resumen)


@login_required
def pedido_confirmacion_view(request, pk):
    try:
        pedido = (
            Pedido.objects.prefetch_related(
                "items__producto",
                "items__solicitud_asesoria__servicio__maestro__usuario",
            )
            .get(pk=pk, usuario=request.user)
        )
    except Pedido.DoesNotExist:
        raise Http404("Pedido no encontrado.")

    movimiento_ferrecredito = (
        MovimientoCredito.objects.select_related("cuenta")
        .filter(
            cuenta__maestro__usuario=request.user,
            tipo=MovimientoCredito.Tipo.COMPRA,
            pedido=pedido,
        )
        .order_by("-creado_en")
        .first()
    )

    if not movimiento_ferrecredito:
        movimiento_ferrecredito = (
            MovimientoCredito.objects.select_related("cuenta")
            .filter(
                cuenta__maestro__usuario=request.user,
                tipo=MovimientoCredito.Tipo.COMPRA,
                descripcion__contains=f"pedido #{pedido.pk}",
            )
            .order_by("-creado_en")
            .first()
        )

    cantidad_cuotas_ferrecredito = None
    if movimiento_ferrecredito:
        match_cuotas = re.search(r"cuotas=(\d+)", movimiento_ferrecredito.descripcion or "")
        if match_cuotas:
            cantidad_cuotas_ferrecredito = int(match_cuotas.group(1))

    pago_webpay = (
        Pago.objects.filter(pedido=pedido, medio_pago=Pago.MedioPago.WEBPAY)
        .order_by("-creado_en")
        .first()
    )

    return render(
        request,
        "pages/confirmacion.html",
        {
            "pedido": pedido,
            "pago_webpay": pago_webpay,
            "movimiento_ferrecredito": movimiento_ferrecredito,
            "cantidad_cuotas_ferrecredito": cantidad_cuotas_ferrecredito,
        },
    )


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
        pedidos_services.aprobar_pedido(pedido, usuario=request.user)
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
        pedidos_services.rechazar_pedido(pedido, usuario=request.user)
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
        pedidos_services.poner_en_preparacion(pedido, usuario=request.user)
        messages.success(request, f"Pedido #{pedido.pk} enviado a bodega para preparación.")
    except ValueError as exc:
        messages.error(request, str(exc))
    return redirect("vendedor_dashboard")


# ─── Dashboard Bodeguero ──────────────────────────────────────────────────────

@_requiere_rol(Usuario.Rol.BODEGUERO, Usuario.Rol.ADMIN)
def bodeguero_dashboard_view(request):
    # Pedidos por estado para el panel de bodeguero
    pedidos_aprobados = (
        Pedido.objects.select_related("usuario").filter(estado=Pedido.Estado.APROBADO).order_by("-creado_en")
    )
    pedidos_en_preparacion = (
        Pedido.objects.select_related("usuario").filter(estado=Pedido.Estado.EN_PREPARACION).order_by("-creado_en")
    )
    pedidos_listos = (
        Pedido.objects.select_related("usuario").filter(estado=Pedido.Estado.LISTO).order_by("-creado_en")
    )
    pedidos_recientes_bodega = (
        Pedido.objects.select_related("usuario").filter(estado__in=[Pedido.Estado.APROBADO, Pedido.Estado.EN_PREPARACION, Pedido.Estado.LISTO]).order_by("-creado_en")[:10]
    )

    # filtros desde query params
    categoria_id = request.GET.get("categoria")
    estado = request.GET.get("estado")
    busqueda = request.GET.get("q")

    productos_stock = inventario_services.obtener_productos_stock_bodega(
        categoria_id=categoria_id, estado=estado, busqueda=busqueda
    )
    productos_bajos = inventario_services.obtener_productos_bajo_stock()
    productos_sin_stock = inventario_services.obtener_productos_sin_stock()
    ultimos_mov = inventario_services.obtener_ultimos_movimientos()
    resumen_stock = inventario_services.obtener_resumen_stock_bodega()
    categorias = Categoria.objects.filter(activa=True)

    return render(
        request,
        "dashboard/bodeguero.html",
        {
            "pedidos_aprobados": pedidos_aprobados,
            "pedidos_en_preparacion": pedidos_en_preparacion,
            "pedidos_listos": pedidos_listos,
            "pedidos_recientes_bodega": pedidos_recientes_bodega,
            "total_aprobados": pedidos_aprobados.count(),
            "total_en_preparacion": pedidos_en_preparacion.count(),
            "total_listos": pedidos_listos.count(),
            "total_pedidos_bodega": (
                pedidos_aprobados.count() + pedidos_en_preparacion.count() + pedidos_listos.count()
            ),
            "productos_stock": productos_stock,
            "productos_bajos": productos_bajos,
            "productos_sin_stock": productos_sin_stock,
            "ultimos_movimientos": ultimos_mov,
            "resumen_stock": resumen_stock,
            "categorias": categorias,
            "filtro_categoria": categoria_id,
            "filtro_estado": estado,
            "filtro_busqueda": busqueda,
        },
    )


@_requiere_rol(Usuario.Rol.BODEGUERO, Usuario.Rol.ADMIN)
def poner_en_preparacion_view(request, pk):
    if request.method != "POST":
        return redirect("bodeguero_dashboard")
    pedido = get_object_or_404(Pedido, pk=pk)
    try:
        pedidos_services.poner_en_preparacion(pedido, usuario=request.user)
        messages.success(request, f"Pedido #{pedido.pk} en preparación.")
    except ValueError as exc:
        messages.error(request, str(exc))
    return redirect("bodeguero_dashboard")


@_requiere_rol(Usuario.Rol.BODEGUERO, Usuario.Rol.ADMIN)
def pedido_entregado_view(request, pk):
    if request.method != "POST":
        return redirect("bodeguero_dashboard")
    pedido = get_object_or_404(Pedido, pk=pk)
    try:
        pedidos_services.marcar_pedido_entregado(pedido, usuario=request.user)
        messages.success(request, f"Pedido #{pedido.pk} marcado como entregado.")
    except ValueError as exc:
        messages.error(request, str(exc))
    return redirect("bodeguero_dashboard")


@_requiere_rol(Usuario.Rol.BODEGUERO, Usuario.Rol.ADMIN)
def marcar_pedido_listo_view(request, pk):
    if request.method != "POST":
        return redirect("bodeguero_dashboard")
    pedido = get_object_or_404(Pedido, pk=pk)
    try:
        pedidos_services.marcar_pedido_listo(pedido, usuario=request.user)
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
