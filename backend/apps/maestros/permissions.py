from rest_framework.permissions import BasePermission


class PlaceholderPermission(BasePermission):
    """Permiso base temporal. Reemplazar por reglas de rol cuando corresponda."""

    def has_permission(self, request, view):
        return True
