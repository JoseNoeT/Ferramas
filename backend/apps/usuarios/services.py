"""Capa de logica de negocio para usuarios."""

from django.contrib.auth import authenticate
from django.db import transaction

from apps.usuarios.forms import UsuarioInternoCreateForm, UsuarioInternoUpdateForm

from .models import Usuario


def registrar_usuario(email: str, password: str) -> Usuario:
    """
    Crea un nuevo usuario con rol cliente.

    Raises ValueError si el email ya existe.
    """
    email = email.strip().lower()
    if Usuario.objects.filter(email=email).exists():
        raise ValueError("Ya existe una cuenta con ese email.")
    usuario = Usuario.objects.create_user(
        email=email,
        password=password,
        rol=Usuario.Rol.CLIENTE,
    )
    return usuario


def autenticar_usuario(email: str, password: str) -> Usuario | None:
    """
    Valida las credenciales y retorna el usuario o None.

    Usa el backend de autenticacion de Django para aprovechar
    el hashing seguro de contrasenas.
    """
    email = email.strip().lower()
    return authenticate(username=email, password=password)


def listar_usuarios_internos():
    """Lista usuarios internos (excluye clientes)."""
    return Usuario.objects.exclude(rol=Usuario.Rol.CLIENTE).order_by("email")


@transaction.atomic
def crear_usuario_interno(data):
    """Crea un usuario interno con contrasena encriptada y rol validado."""
    form = UsuarioInternoCreateForm(data=data)
    if not form.is_valid():
        return None, form

    usuario = Usuario.objects.create_user(
        email=form.cleaned_data["email"],
        password=form.cleaned_data["password_temporal"],
        rol=form.cleaned_data["rol"],
        activo=form.cleaned_data["activo"],
        is_active=form.cleaned_data["activo"],
        is_staff=form.cleaned_data["rol"] == Usuario.Rol.ADMIN,
    )
    return usuario, form


@transaction.atomic
def actualizar_usuario_interno(usuario, data):
    """Actualiza email, rol y estado de un usuario interno."""
    form = UsuarioInternoUpdateForm(data=data, instance=usuario)
    if not form.is_valid():
        return None, form

    usuario = form.save(commit=False)
    usuario.is_active = usuario.activo
    usuario.is_staff = usuario.rol == Usuario.Rol.ADMIN
    usuario.save()
    return usuario, form


def cambiar_estado_usuario(usuario, activo):
    """Activa o desactiva usuario interno para login."""
    usuario.activo = bool(activo)
    usuario.is_active = bool(activo)
    usuario.save(update_fields=["activo", "is_active"])
    return usuario
