from django.db import transaction

from apps.catalogo.forms import CategoriaForm, ProductoForm
from apps.catalogo.models import Categoria, Producto


def obtener_productos_activos():
    """Retorna todos los productos activos con su categoria."""
    return Producto.objects.filter(activo=True).select_related("categoria")


def obtener_producto_por_slug(slug):
    """Retorna un producto activo por su slug, o None si no existe."""
    try:
        return Producto.objects.select_related("categoria").get(slug=slug, activo=True)
    except Producto.DoesNotExist:
        return None


def listar_productos_admin():
    """Retorna todos los productos para dashboard administrativo."""
    return Producto.objects.select_related("categoria").all()


def listar_categorias():
    """Retorna categorias activas para uso en formularios y filtros."""
    return Categoria.objects.filter(activa=True).order_by("nombre")


def listar_categorias_admin():
    """Retorna todas las categorias para gestión administrativa."""
    return Categoria.objects.order_by("nombre")


@transaction.atomic
def crear_producto(data, files=None):
    """Crea un producto usando validaciones del formulario de dominio."""
    form = ProductoForm(data=data, files=files)
    if not form.is_valid():
        return None, form
    producto = form.save()
    return producto, form


@transaction.atomic
def actualizar_producto(producto, data, files=None):
    """Actualiza un producto existente usando validaciones del formulario."""
    form = ProductoForm(data=data, files=files, instance=producto)
    if not form.is_valid():
        return None, form
    producto = form.save()
    return producto, form


def cambiar_estado_producto(producto, activo):
    """Activa o desactiva un producto del catalogo."""
    producto.activo = bool(activo)
    producto.save(update_fields=["activo"])
    return producto


@transaction.atomic
def crear_categoria(data):
    """Crea una categoria con validaciones del formulario de dominio."""
    form = CategoriaForm(data=data)
    if not form.is_valid():
        return None, form
    categoria = form.save()
    return categoria, form
