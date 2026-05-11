from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework import viewsets

from apps.maestros.forms import (
    RegistroMaestroPymeForm,
    ServicioMaestroForm,
    SolicitudAsesoriaForm,
)
from apps.maestros.models import PerfilMaestroPyme, ServicioMaestro, SolicitudAsesoria
from apps.maestros.services import (
    aprobar_maestro_pyme,
    crear_servicio_maestro,
    crear_solicitud_asesoria,
    rechazar_maestro_pyme,
    registrar_maestro_pyme,
)
from apps.usuarios.views import _requiere_admin


class PlaceholderViewSet(viewsets.ViewSet):
    """ViewSet base temporal para enrutar endpoints de la app maestros."""

    # TODO: Reemplazar por ViewSets reales por recurso.
    pass


@login_required
def registro_maestro_pyme_view(request):
    if request.method == "POST":
        form = RegistroMaestroPymeForm(request.POST)
        if form.is_valid():
            registrar_maestro_pyme(request.user, form.cleaned_data)
            messages.success(
                request,
                "Registro Maestro/PYME enviado correctamente. Estado: pendiente.",
            )
            form = RegistroMaestroPymeForm()
        else:
            messages.error(request, "Corrige los campos indicados para continuar.")
    else:
        perfil = PerfilMaestroPyme.objects.filter(usuario=request.user).first()
        form = RegistroMaestroPymeForm(instance=perfil)

    return render(request, "pages/registro-maestro-pyme.html", {"form": form})


@login_required
def panel_maestro_pyme_view(request):
    perfil_maestro = PerfilMaestroPyme.objects.filter(usuario=request.user).first()

    if not perfil_maestro:
        return render(
            request,
            "pages/panel-maestro-pyme.html",
            {
                "perfil_maestro": None,
                "maestro_aprobado": False,
                "total_servicios": 0,
                "servicios_activos": 0,
                "total_solicitudes": 0,
            },
        )

    servicios = ServicioMaestro.objects.filter(maestro=perfil_maestro)
    total_servicios = servicios.count()
    servicios_activos = servicios.filter(activo=True).count()
    total_solicitudes = SolicitudAsesoria.objects.filter(servicio__maestro=perfil_maestro).count()
    maestro_aprobado = perfil_maestro.estado == PerfilMaestroPyme.Estado.APROBADO

    return render(
        request,
        "pages/panel-maestro-pyme.html",
        {
            "perfil_maestro": perfil_maestro,
            "maestro_aprobado": maestro_aprobado,
            "total_servicios": total_servicios,
            "servicios_activos": servicios_activos,
            "total_solicitudes": total_solicitudes,
        },
    )


@login_required
def publicar_servicio_maestro_view(request):
    if request.method == "POST":
        form = ServicioMaestroForm(request.POST)
        if form.is_valid():
            perfil = PerfilMaestroPyme.objects.filter(usuario=request.user).first()
            if not perfil:
                messages.error(
                    request,
                    "Debes registrar tu perfil Maestro/PYME antes de publicar servicios.",
                )
            else:
                try:
                    crear_servicio_maestro(perfil, form.cleaned_data)
                    messages.success(request, "Servicio publicado correctamente.")
                    form = ServicioMaestroForm()
                except ValueError:
                    messages.error(
                        request,
                        "Tu perfil Maestro/PYME debe estar aprobado para publicar servicios.",
                    )
        else:
            messages.error(request, "Corrige los campos indicados para continuar.")
    else:
        form = ServicioMaestroForm()

    return render(request, "pages/publicar-servicio-maestro.html", {"form": form})


@login_required
def mis_servicios_maestro_view(request):
    perfil_maestro = PerfilMaestroPyme.objects.filter(usuario=request.user).first()

    if not perfil_maestro:
        return render(
            request,
            "pages/mis-servicios-maestro.html",
            {
                "perfil_maestro": None,
                "servicios": [],
            },
        )

    servicios = ServicioMaestro.objects.filter(maestro=perfil_maestro).order_by("-creado_en")
    return render(
        request,
        "pages/mis-servicios-maestro.html",
        {
            "perfil_maestro": perfil_maestro,
            "servicios": servicios,
        },
    )


def servicios_maestros_view(request):
    servicios = (
        ServicioMaestro.objects.filter(
            activo=True,
            maestro__estado=PerfilMaestroPyme.Estado.APROBADO,
        )
        .select_related("maestro", "maestro__usuario")
        .order_by("-creado_en")
    )
    return render(
        request,
        "pages/servicios-maestros.html",
        {
            "servicios": servicios,
            "total_servicios": servicios.count(),
        },
    )


@login_required
def solicitud_asesoria_maestro_view(request):
    messages.info(request, "Selecciona un servicio para solicitar asesoría.")
    return redirect("servicios_maestros")


@login_required
def solicitud_asesoria_maestro_detalle_view(request, servicio_id):
    servicio = get_object_or_404(
        ServicioMaestro.objects.select_related("maestro", "maestro__usuario"),
        pk=servicio_id,
        activo=True,
        maestro__estado=PerfilMaestroPyme.Estado.APROBADO,
    )

    if request.method == "POST":
        form = SolicitudAsesoriaForm(request.POST)
        if form.is_valid():
            try:
                crear_solicitud_asesoria(request.user, servicio, form.cleaned_data)
                messages.success(request, "Solicitud de asesoría creada correctamente.")
                return redirect("solicitud_asesoria_maestro_detalle", servicio_id=servicio.pk)
            except ValueError:
                messages.error(request, "El servicio seleccionado no se encuentra disponible.")
        else:
            messages.error(request, "Corrige los campos indicados para continuar.")
    else:
        form = SolicitudAsesoriaForm()

    return render(
        request,
        "pages/solicitud-asesoria-maestro.html",
        {
            "form": form,
            "servicio": servicio,
            "cargo_confirmacion": 5000,
        },
    )


@_requiere_admin
def admin_maestros_view(request):
    perfiles = (
        PerfilMaestroPyme.objects.select_related("usuario")
        .prefetch_related("servicios")
        .all()
        .order_by("-creado_en")
    )
    total_perfiles = perfiles.count()
    total_pendientes = perfiles.filter(estado=PerfilMaestroPyme.Estado.PENDIENTE).count()
    total_aprobados = perfiles.filter(estado=PerfilMaestroPyme.Estado.APROBADO).count()
    total_rechazados = perfiles.filter(estado=PerfilMaestroPyme.Estado.RECHAZADO).count()

    return render(
        request,
        "dashboard/admin-maestros.html",
        {
            "perfiles": perfiles,
            "total_perfiles": total_perfiles,
            "total_pendientes": total_pendientes,
            "total_aprobados": total_aprobados,
            "total_rechazados": total_rechazados,
        },
    )


@_requiere_admin
def aprobar_maestro_pyme_admin_view(request, pk):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    perfil = get_object_or_404(PerfilMaestroPyme, pk=pk)
    aprobar_maestro_pyme(perfil)
    messages.success(request, f"Perfil Maestro/PYME de '{perfil.usuario.email}' aprobado correctamente.")
    return redirect("admin_maestros")


@_requiere_admin
def rechazar_maestro_pyme_admin_view(request, pk):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    perfil = get_object_or_404(PerfilMaestroPyme, pk=pk)
    rechazar_maestro_pyme(perfil)
    messages.success(request, f"Perfil Maestro/PYME de '{perfil.usuario.email}' rechazado correctamente.")
    return redirect("admin_maestros")
