from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from apps.catalogo import services as catalogo_services
from apps.catalogo.forms import CategoriaForm, ProductoForm
from apps.catalogo.models import Producto
from apps.usuarios.models import Usuario


def _requiere_admin(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.rol != Usuario.Rol.ADMIN:
            return HttpResponseForbidden("No tienes permiso para acceder a esta sección.")
        return view_func(request, *args, **kwargs)

    return wrapper


@login_required
def catalogo_view(request):
    productos = catalogo_services.obtener_productos_activos()
    return render(request, "pages/catalogo.html", {"productos": productos})


@login_required
def producto_detalle_view(request, slug):
    producto = catalogo_services.obtener_producto_por_slug(slug)
    if producto is None:
        raise Http404("Producto no encontrado.")
    return render(request, "pages/producto.html", {"producto": producto})


@_requiere_admin
def admin_productos_dashboard_view(request):
    productos = catalogo_services.listar_productos_admin()
    return render(request, "dashboard/admin-productos.html", {"productos": productos})


@_requiere_admin
def crear_producto_view(request):
    if request.method == "POST":
        producto, form = catalogo_services.crear_producto(request.POST, request.FILES)
        if producto:
            messages.success(request, f"Producto '{producto.nombre}' creado correctamente.")
            return redirect("admin_productos_dashboard")
        messages.error(request, "Revisa los datos del formulario.")
    else:
        form = ProductoForm()

    return render(
        request,
        "dashboard/admin-producto-form.html",
        {
            "form": form,
            "modo": "crear",
            "titulo": "Crear producto",
        },
    )


@_requiere_admin
def editar_producto_view(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == "POST":
        producto_actualizado, form = catalogo_services.actualizar_producto(
            producto,
            request.POST,
            request.FILES,
        )
        if producto_actualizado:
            messages.success(
                request,
                f"Producto '{producto_actualizado.nombre}' actualizado correctamente.",
            )
            return redirect("admin_productos_dashboard")
        messages.error(request, "Revisa los datos del formulario.")
    else:
        form = ProductoForm(instance=producto)

    return render(
        request,
        "dashboard/admin-producto-form.html",
        {
            "form": form,
            "modo": "editar",
            "titulo": f"Editar producto: {producto.nombre}",
            "producto": producto,
        },
    )


@_requiere_admin
def cambiar_estado_producto_view(request, pk):
    if request.method != "POST":
        return redirect("admin_productos_dashboard")

    producto = get_object_or_404(Producto, pk=pk)
    nuevo_estado = request.POST.get("activo") == "1"
    catalogo_services.cambiar_estado_producto(producto, nuevo_estado)

    if nuevo_estado:
        messages.success(request, f"Producto '{producto.nombre}' activado.")
    else:
        messages.warning(request, f"Producto '{producto.nombre}' desactivado.")

    return redirect("admin_productos_dashboard")


@_requiere_admin
def admin_categorias_dashboard_view(request):
    if request.method == "POST":
        categoria, form = catalogo_services.crear_categoria(request.POST)
        if categoria:
            messages.success(request, f"Categoria '{categoria.nombre}' creada correctamente.")
            return redirect("admin_categorias_dashboard")
        messages.error(request, "Revisa los datos de la categoria.")
    else:
        form = CategoriaForm()

    categorias = catalogo_services.listar_categorias_admin()
    return render(
        request,
        "dashboard/admin-categorias.html",
        {
            "form": form,
            "categorias": categorias,
        },
    )
