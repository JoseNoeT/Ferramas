from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from apps.usuarios.services import (
    crear_usuario_interno,
    actualizar_usuario_interno,
    listar_usuarios_internos,
    cambiar_estado_usuario,
)


def admin_dashboard_view(request):
    from .admin_services import obtener_dashboard_indicadores

    context = obtener_dashboard_indicadores()
    return render(request, "dashboard/administrador.html", context)


def admin_usuarios_dashboard_view(request):
    usuarios = listar_usuarios_internos()
    return render(request, "dashboard/admin-usuarios.html", {"usuarios": usuarios})


def crear_usuario_interno_view(request):
    if request.method == "POST":
        usuario, form = crear_usuario_interno(request.POST)
        if usuario:
            messages.success(request, f"Usuario interno '{usuario.email}' creado correctamente.")
            return redirect("admin_usuarios_dashboard")
        messages.error(request, "Revisa los datos del formulario.")
    else:
        from .forms import UsuarioInternoCreateForm

        form = UsuarioInternoCreateForm()

    return render(
        request,
        "dashboard/admin-usuario-form.html",
        {
            "form": form,
            "titulo": "Crear usuario interno",
            "modo": "crear",
        },
    )


def editar_usuario_interno_view(request, pk):
    from .models import Usuario

    usuario_obj = get_object_or_404(Usuario, pk=pk)

    if usuario_obj.rol == Usuario.Rol.CLIENTE:
        messages.error(request, "No se permite editar clientes desde este dashboard.")
        return redirect("admin_usuarios_dashboard")

    if request.method == "POST":
        usuario_actualizado, form = actualizar_usuario_interno(usuario_obj, request.POST)
        if usuario_actualizado:
            messages.success(request, f"Usuario '{usuario_actualizado.email}' actualizado.")
            return redirect("admin_usuarios_dashboard")
        messages.error(request, "Revisa los datos del formulario.")
    else:
        from .forms import UsuarioInternoUpdateForm

        form = UsuarioInternoUpdateForm(instance=usuario_obj)

    return render(
        request,
        "dashboard/admin-usuario-form.html",
        {
            "form": form,
            "titulo": f"Editar usuario: {usuario_obj.email}",
            "modo": "editar",
            "usuario_obj": usuario_obj,
        },
    )


def cambiar_estado_usuario_view(request, pk):
    from .models import Usuario

    if request.method != "POST":
        return redirect("admin_usuarios_dashboard")

    usuario_obj = get_object_or_404(Usuario, pk=pk)

    if usuario_obj.rol == Usuario.Rol.CLIENTE:
        messages.error(request, "No se permite gestionar clientes desde este dashboard.")
        return redirect("admin_usuarios_dashboard")

    nuevo_estado = request.POST.get("activo") == "1"
    cambiar_estado_usuario(usuario_obj, nuevo_estado)

    if nuevo_estado:
        messages.success(request, f"Usuario '{usuario_obj.email}' activado.")
    else:
        messages.warning(request, f"Usuario '{usuario_obj.email}' desactivado.")

    return redirect("admin_usuarios_dashboard")
