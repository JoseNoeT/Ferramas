from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render
from django.utils import timezone
from apps.credito import services as credito_services
from apps.credito.models import CuentaCredito, CuotaCredito, SolicitudFerreCredito
from apps.maestros.models import PerfilMaestroPyme
from apps.usuarios.views import _requiere_admin
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import viewsets


class VistaPlaceholder(viewsets.ViewSet):
    """ViewSet temporal de la app credito."""

    # TODO: Reemplazar por ViewSets reales por recurso.
    pass


def _obtener_perfil_y_cuenta_credito(usuario):
    perfil = PerfilMaestroPyme.objects.filter(usuario=usuario).first()
    if not perfil:
        return None, None, Response(
            {"detail": "No tienes perfil Maestro/PYME asociado."},
            status=status.HTTP_403_FORBIDDEN,
        )

    if perfil.estado != PerfilMaestroPyme.Estado.APROBADO:
        return perfil, None, Response(
            {"detail": "Tu perfil Maestro/PYME no está aprobado."},
            status=status.HTTP_403_FORBIDDEN,
        )

    cuenta = CuentaCredito.objects.filter(maestro=perfil).first()
    if not cuenta:
        return perfil, None, Response(
            {"detail": "No tienes cuenta de crédito asociada."},
            status=status.HTTP_404_NOT_FOUND,
        )

    return perfil, cuenta, None


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def saldo_cuenta_corriente_view(request):
    perfil, cuenta, error_response = _obtener_perfil_y_cuenta_credito(request.user)
    if error_response is not None:
        return error_response

    saldo_disponible = cuenta.saldo_disponible
    puede_comprar = (
        cuenta.estado == CuentaCredito.Estado.ACTIVA
        and saldo_disponible > 0
        and not credito_services.tiene_cuotas_vencidas(cuenta)
    )

    return Response(
        {
            "usuario_id": request.user.id,
            "perfil_id": perfil.id,
            "tipo": perfil.tipo,
            "estado_perfil": perfil.estado,
            "cuenta_id": cuenta.id,
            "estado_cuenta": cuenta.estado,
            "cupo_aprobado": str(cuenta.cupo_aprobado),
            "saldo_usado": str(cuenta.saldo_usado),
            "saldo_disponible": str(saldo_disponible),
            "puede_comprar": puede_comprar,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def total_deuda_cuenta_corriente_view(request):
    _, cuenta, error_response = _obtener_perfil_y_cuenta_credito(request.user)
    if error_response is not None:
        return error_response

    hoy = timezone.localdate()
    cuotas_consideradas = CuotaCredito.objects.filter(cuenta=cuenta).filter(
        Q(estado=CuotaCredito.Estado.PENDIENTE) | Q(estado=CuotaCredito.Estado.VENCIDA)
    )
    cuotas_pendientes = CuotaCredito.objects.filter(
        cuenta=cuenta,
        estado=CuotaCredito.Estado.PENDIENTE,
    ).count()
    cuotas_vencidas_qs = CuotaCredito.objects.filter(cuenta=cuenta).filter(
        Q(estado=CuotaCredito.Estado.VENCIDA)
        | Q(estado=CuotaCredito.Estado.PENDIENTE, fecha_vencimiento__lt=hoy)
    )
    cuotas_vencidas = cuotas_vencidas_qs.count()
    monto_vencido = cuotas_vencidas_qs.aggregate(total=Sum("monto"))["total"] or 0
    total_deuda = cuotas_consideradas.aggregate(total=Sum("monto"))["total"] or 0

    return Response(
        {
            "usuario_id": request.user.id,
            "cuenta_id": cuenta.id,
            "total_deuda": str(total_deuda),
            "saldo_usado": str(cuenta.saldo_usado),
            "cuotas_pendientes": cuotas_pendientes,
            "cuotas_vencidas": cuotas_vencidas,
            "monto_vencido": str(monto_vencido),
            "al_dia": cuotas_vencidas == 0,
        },
        status=status.HTTP_200_OK,
    )


@login_required
def solicitud_ferrecredito_view(request):
    perfil_maestro = PerfilMaestroPyme.objects.filter(usuario=request.user).first()
    solicitud_pendiente = None
    cuenta_credito = None

    if perfil_maestro:
        solicitud_pendiente = (
            SolicitudFerreCredito.objects.filter(
                maestro=perfil_maestro,
                estado=SolicitudFerreCredito.Estado.PENDIENTE,
            )
            .order_by("-creado_en")
            .first()
        )
        cuenta_credito = CuentaCredito.objects.filter(maestro=perfil_maestro).first()

    if request.method == "POST":
        if not perfil_maestro:
            messages.error(request, "Debes registrarte como Maestro/PYME para solicitar FerreCrédito.")
            return redirect("solicitud_ferrecredito")

        if perfil_maestro.estado != PerfilMaestroPyme.Estado.APROBADO:
            messages.error(request, "Tu perfil Maestro/PYME debe estar aprobado por administrador.")
            return redirect("solicitud_ferrecredito")

        try:
            credito_services.crear_solicitud_ferrecredito(request.user, request.POST)
            messages.success(request, "Solicitud FerreCrédito enviada correctamente.")
            return redirect("estado_ferrecredito")
        except ValueError as exc:
            messages.error(request, str(exc))

    return render(
        request,
        "pages/solicitud-ferrecredito.html",
        {
            "perfil_maestro": perfil_maestro,
            "solicitud_pendiente": solicitud_pendiente,
            "cuenta_credito": cuenta_credito,
        },
    )


@login_required
def estado_ferrecredito_view(request):
    return render(request, "pages/estado-ferrecredito.html")


@_requiere_admin
def admin_credito_view(request):
    resumen = credito_services.obtener_resumen_admin_credito()
    return render(request, "dashboard/admin-credito.html", resumen)


@_requiere_admin
def aprobar_solicitud_ferrecredito_admin_view(request, pk):
    if request.method != "POST":
        return redirect("admin_credito")

    solicitud = get_object_or_404(SolicitudFerreCredito, pk=pk)
    cupo_aprobado = request.POST.get("cupo_aprobado")
    observacion_admin = request.POST.get("observacion_admin", "")

    try:
        credito_services.aprobar_solicitud_ferrecredito(
            solicitud,
            cupo_aprobado,
            observacion_admin,
        )
        messages.success(request, f"Solicitud #{solicitud.pk} aprobada correctamente.")
    except ValueError as exc:
        messages.error(request, str(exc))

    return redirect("admin_credito")


@_requiere_admin
def rechazar_solicitud_ferrecredito_admin_view(request, pk):
    if request.method != "POST":
        return redirect("admin_credito")

    solicitud = get_object_or_404(SolicitudFerreCredito, pk=pk)
    observacion_admin = request.POST.get("observacion_admin", "")

    try:
        credito_services.rechazar_solicitud_ferrecredito(solicitud, observacion_admin)
        messages.success(request, f"Solicitud #{solicitud.pk} rechazada correctamente.")
    except ValueError as exc:
        messages.error(request, str(exc))

    return redirect("admin_credito")

