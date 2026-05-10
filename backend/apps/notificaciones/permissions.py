from rest_framework.permissions import BasePermission


class PermisoPlaceholder(BasePermission):
    """Permiso temporal de la app notificaciones."""

    def has_permission(self, request, view):
        return True

