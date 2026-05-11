from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from rest_framework import viewsets

from apps.maestros.forms import (
    RegistroMaestroPymeForm,
    ServicioMaestroForm,
    SolicitudAsesoriaForm,
)
from apps.maestros.models import PerfilMaestroPyme, ServicioMaestro
from apps.maestros.services import (
    crear_servicio_maestro,
    crear_solicitud_asesoria,
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


def panel_maestro_pyme_view(request):
    return render(request, "pages/panel-maestro-pyme.html")


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


def mis_servicios_maestro_view(request):
    return render(request, "pages/mis-servicios-maestro.html")


def servicios_maestros_view(request):
    return render(request, "pages/servicios-maestros.html")


@login_required
def solicitud_asesoria_maestro_view(request):
    servicio_demo = ServicioMaestro.objects.filter(activo=True).select_related("maestro").first()

    if request.method == "POST":
        form = SolicitudAsesoriaForm(request.POST)
        if not servicio_demo:
            messages.error(request, "No hay servicios activos disponibles para solicitar asesoría.")
        elif form.is_valid():
            try:
                crear_solicitud_asesoria(request.user, servicio_demo, form.cleaned_data)
                messages.success(request, "Solicitud de asesoría creada correctamente.")
                form = SolicitudAsesoriaForm()
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
            "servicio_demo": servicio_demo,
        },
    )


@_requiere_admin
def admin_maestros_view(request):
    return render(request, "dashboard/admin-maestros.html")
