from django.contrib import messages
from django.shortcuts import render
from apps.usuarios.views import _requiere_admin
from rest_framework import viewsets


class PlaceholderViewSet(viewsets.ViewSet):
    """ViewSet base temporal para enrutar endpoints de la app maestros."""

    # TODO: Reemplazar por ViewSets reales por recurso.
    pass


def registro_maestro_pyme_view(request):
    if request.method == "POST":
        messages.info(
            request,
            "Registro recibido en modo demostracion. "
            "La logica backend sera implementada despues.",
        )

    return render(request, "pages/registro-maestro-pyme.html")


def panel_maestro_pyme_view(request):
    return render(request, "pages/panel-maestro-pyme.html")


def publicar_servicio_maestro_view(request):
    if request.method == "POST":
        messages.info(
            request,
            "Servicio recibido en modo demostracion. "
            "La logica backend sera implementada despues.",
        )

    return render(request, "pages/publicar-servicio-maestro.html")


def mis_servicios_maestro_view(request):
    return render(request, "pages/mis-servicios-maestro.html")


def servicios_maestros_view(request):
    return render(request, "pages/servicios-maestros.html")


def solicitud_asesoria_maestro_view(request):
    if request.method == "POST":
        messages.info(
            request,
            "Solicitud de asesoría recibida en modo demostración. "
            "La lógica backend será implementada después.",
        )

    return render(request, "pages/solicitud-asesoria-maestro.html")


@_requiere_admin
def admin_maestros_view(request):
    return render(request, "dashboard/admin-maestros.html")
