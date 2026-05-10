from django.contrib import messages
from django.shortcuts import render
from apps.usuarios.views import _requiere_admin
from rest_framework import viewsets


class VistaPlaceholder(viewsets.ViewSet):
    """ViewSet temporal de la app encuestas."""

    # TODO: Reemplazar por ViewSets reales por recurso.
    pass


def encuesta_satisfaccion_view(request):
    if request.method == "POST":
        messages.info(
            request,
            "Encuesta recibida en modo demostracion. "
            "La logica backend sera implementada despues.",
        )

    return render(request, "pages/encuesta-satisfaccion.html")


@_requiere_admin
def admin_encuestas_view(request):
    return render(request, "dashboard/admin-encuestas.html")

