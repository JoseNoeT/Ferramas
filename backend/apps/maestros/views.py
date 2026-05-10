from django.contrib import messages
from django.shortcuts import render
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
