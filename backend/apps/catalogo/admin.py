from django.contrib import admin

from apps.catalogo.models import Categoria, Producto


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "slug", "activa")
    prepopulated_fields = {"slug": ("nombre",)}
    list_editable = ("activa",)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "precio", "stock", "activo", "categoria", "fecha_creacion")
    prepopulated_fields = {"slug": ("nombre",)}
    list_editable = ("precio", "stock", "activo")
    list_filter = ("activo", "categoria")
    search_fields = ("nombre",)
