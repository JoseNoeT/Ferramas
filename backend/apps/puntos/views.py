from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from apps.usuarios.views import _requiere_admin
from rest_framework import viewsets


class VistaPlaceholder(viewsets.ViewSet):
    """ViewSet temporal de la app puntos."""

    # TODO: Reemplazar por ViewSets reales por recurso.
    pass


@_requiere_admin
def admin_puntos_view(request):
    return render(request, "dashboard/admin-puntos.html")


@login_required
def mis_puntos_view(request):
    return render(request, "pages/mis-puntos.html")

