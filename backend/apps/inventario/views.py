from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.catalogo.models import Producto
from django.http import HttpResponseForbidden, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from functools import wraps
from apps.inventario import services as inventario_services
from apps.inventario.models import MovimientoInventario
from apps.usuarios.models import Usuario


def _requiere_rol_bodeguero(func):
    @wraps(func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.rol not in (Usuario.Rol.BODEGUERO, Usuario.Rol.ADMIN):
            return HttpResponseForbidden("No tienes permiso para ajustar stock.")
        return func(request, *args, **kwargs)

    return wrapper


@_requiere_rol_bodeguero
def ajustar_stock_view(request):
    if request.method != "POST":
        return HttpResponseForbidden("Método no permitido")

    producto_id = request.POST.get("producto_id")
    cantidad = request.POST.get("cantidad")
    tipo = request.POST.get("tipo_movimiento")
    motivo = request.POST.get("motivo", "").strip()

    if not producto_id or cantidad is None or not tipo or not motivo:
        messages.error(request, "Parámetros insuficientes o motivo vacío.")
        return redirect("bodeguero_dashboard")

    try:
        producto = inventario_services.ajustar_stock_producto(
            producto_id=int(producto_id),
            cantidad=int(cantidad),
            tipo_movimiento=tipo,
            motivo=motivo,
            usuario=request.user,
        )
        messages.success(request, f"Stock de {producto.nombre} actualizado: {producto.stock}.")
    except Producto.DoesNotExist:
        raise Http404("Producto no encontrado.")
    except ValueError as exc:
        messages.error(request, str(exc))

    return redirect("bodeguero_dashboard")


class VistaPlaceholder(viewsets.ViewSet):
    """ViewSet temporal de la app inventario."""

    # TODO: Reemplazar por ViewSets reales por recurso.
    pass


@api_view(["GET"])
@permission_classes([AllowAny])
def stock_disponible_producto_view(request, producto_id):
    producto = Producto.objects.filter(pk=producto_id, activo=True).first()
    if not producto:
        return Response({"detail": "Producto no encontrado."}, status=status.HTTP_404_NOT_FOUND)

    disponible = producto.stock > 0
    return Response(
        {
            "producto_id": producto.id,
            "nombre": producto.nombre,
            "activo": producto.activo,
            "stock_disponible": producto.stock,
            "disponible": disponible,
        },
        status=status.HTTP_200_OK,
    )

