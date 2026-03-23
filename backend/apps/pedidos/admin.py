from django.contrib import admin

from apps.pedidos.models import Carrito, ItemCarrito, ItemPedido, Pedido


class ItemCarritoInline(admin.TabularInline):
    model = ItemCarrito
    extra = 0


@admin.register(Carrito)
class CarritoAdmin(admin.ModelAdmin):
    list_display = ("usuario", "creado_en", "actualizado_en")
    inlines = [ItemCarritoInline]


@admin.register(ItemCarrito)
class ItemCarritoAdmin(admin.ModelAdmin):
    list_display = ("carrito", "producto", "cantidad")
    list_select_related = ("carrito", "producto")


class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0
    readonly_fields = ("precio_unitario",)


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ("pk", "usuario", "estado", "tipo_entrega", "total", "creado_en")
    list_filter = ("estado", "tipo_entrega")
    list_editable = ("estado",)
    inlines = [ItemPedidoInline]
    readonly_fields = ("subtotal", "total", "creado_en")


@admin.register(ItemPedido)
class ItemPedidoAdmin(admin.ModelAdmin):
    list_display = ("pedido", "producto", "cantidad", "precio_unitario")
    list_select_related = ("pedido", "producto")
