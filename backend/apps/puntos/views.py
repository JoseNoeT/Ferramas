from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Count, Sum
from apps.usuarios.views import _requiere_admin
from rest_framework import viewsets

from apps.puntos.models import CuentaPuntos, MovimientoPuntos
from apps.puntos.services import obtener_resumen_puntos


class VistaPlaceholder(viewsets.ViewSet):
    """ViewSet temporal de la app puntos."""

    # TODO: Reemplazar por ViewSets reales por recurso.
    pass


@_requiere_admin
def admin_puntos_view(request):
    cuentas = (
        CuentaPuntos.objects.select_related("usuario")
        .annotate(cantidad_movimientos=Count("movimientos"))
        .order_by("-actualizado_en")
    )
    resumen = {
        "total_cuentas": cuentas.count(),
        "total_puntos_circulacion": cuentas.aggregate(total=Sum("saldo"))["total"] or 0,
        "total_movimientos": MovimientoPuntos.objects.count(),
    }
    return render(
        request,
        "dashboard/admin-puntos.html",
        {
            "cuentas": cuentas,
            **resumen,
        },
    )


@login_required
def mis_puntos_view(request):
    contexto = obtener_resumen_puntos(request.user)
    return render(request, "pages/mis-puntos.html", contexto)

