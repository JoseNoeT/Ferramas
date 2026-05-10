from rest_framework.permissions import BasePermission


class PermisoPlaceholder(BasePermission):
    """Permiso temporal para la app pedidos."""

    def has_permission(self, request, view):
        return True
