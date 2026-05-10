from django.contrib import messages
from django.shortcuts import render
from apps.usuarios.views import _requiere_admin
from rest_framework import viewsets


class VistaPlaceholder(viewsets.ViewSet):
    """ViewSet temporal de la app credito."""

    # TODO: Reemplazar por ViewSets reales por recurso.
    pass


def solicitud_ferrecredito_view(request):
    if request.method == "POST":
        messages.info(
            request,
            "Solicitud FerreCrédito recibida en modo demostración. "
            "La lógica backend será implementada después.",
        )

    return render(request, "pages/solicitud-ferrecredito.html")


def estado_ferrecredito_view(request):
    return render(request, "pages/estado-ferrecredito.html")


@_requiere_admin
def admin_credito_view(request):
    return render(request, "dashboard/admin-credito.html")

