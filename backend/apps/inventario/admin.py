from django.contrib import admin

from apps.inventario.models import MovimientoInventario


@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
	list_display = (
		"producto",
		"pedido",
		"tipo_movimiento",
		"cantidad",
		"stock_anterior",
		"stock_nuevo",
		"usuario",
		"fecha_creacion",
	)
	list_filter = ("tipo_movimiento", "fecha_creacion")
	search_fields = ("producto__nombre", "pedido__id", "motivo", "usuario__email")
	readonly_fields = (
		"producto",
		"pedido",
		"tipo_movimiento",
		"cantidad",
		"stock_anterior",
		"stock_nuevo",
		"usuario",
		"motivo",
		"fecha_creacion",
	)
