from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.catalogo import services as catalogo_services
from apps.catalogo.forms import CategoriaForm, ProductoForm
from apps.catalogo.models import Producto
from apps.catalogo.serializers import ProductoSerializers
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


@login_required
def ofertas_view(request):
    ahora = timezone.now()
    productos = (
        Producto.objects.filter(
            activo=True,
            en_oferta=True,
            fecha_inicio_oferta__lte=ahora,
            fecha_fin_oferta__gte=ahora,
        )
        .select_related("categoria")
        .order_by("nombre")
    )
    
    # Calcular descuentos y preparar datos enriquecidos
    productos_enriquecidos = []
    for producto in productos:
        descuento_porcentaje = 0
        if producto.precio_oferta and producto.precio:
            descuento_porcentaje = round(
                ((producto.precio - producto.precio_oferta) / producto.precio) * 100
            )
        productos_enriquecidos.append({
            "obj": producto,
            "descuento_porcentaje": descuento_porcentaje,
        })
    
    # Separar productos destacados (top 5 con mayor descuento)
    productos_destacados = sorted(
        productos_enriquecidos,
        key=lambda x: x["descuento_porcentaje"],
        reverse=True
    )[:5]
    
    # Obtener categorías con ofertas
    categorias = set(p["obj"].categoria.nombre for p in productos_enriquecidos if p["obj"].categoria)
    categorias_ordenadas = sorted(list(categorias))
    
    # Ordenamiento solicitado (por defecto: mayor descuento)
    ordenamiento = request.GET.get("ordenar", "descuento")
    productos_filtrados = productos_enriquecidos
    
    if ordenamiento == "precio_menor":
        productos_filtrados = sorted(productos_filtrados, key=lambda x: x["obj"].precio_oferta or x["obj"].precio)
    elif ordenamiento == "precio_mayor":
        productos_filtrados = sorted(productos_filtrados, key=lambda x: x["obj"].precio_oferta or x["obj"].precio, reverse=True)
    elif ordenamiento == "nombre":
        productos_filtrados = sorted(productos_filtrados, key=lambda x: x["obj"].nombre)
    else:  # "descuento" por defecto
        productos_filtrados = sorted(productos_filtrados, key=lambda x: x["descuento_porcentaje"], reverse=True)
    
    # Filtrar por categoría si se selecciona
    categoria_filtro = request.GET.get("categoria", "")
    if categoria_filtro and categoria_filtro != "todas":
        productos_filtrados = [p for p in productos_filtrados if p["obj"].categoria and p["obj"].categoria.nombre == categoria_filtro]
    
    return render(
        request,
        "pages/ofertas.html",
        {
            "productos": productos_filtrados,
            "productos_destacados": productos_destacados,
            "categorias": categorias_ordenadas,
            "ordenamiento_actual": ordenamiento,
            "categoria_actual": categoria_filtro,
        }
    )


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

#------------webservices REST.---------------#


@api_view(["GET"])
def api_producto_detalle_view(request, pk):
    """Retorna detalle de un producto activo por id."""
    producto = get_object_or_404(Producto.objects.select_related("categoria"), pk=pk, activo=True)
    serializer = ProductoSerializers(producto)
    return Response(serializer.data, status=status.HTTP_200_OK)

