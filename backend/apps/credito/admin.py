from django.contrib import admin

from apps.credito.models import CuentaCredito, CuotaCredito, MovimientoCredito


@admin.register(CuentaCredito)
class CuentaCreditoAdmin(admin.ModelAdmin):
	list_display = (
		"maestro",
		"cupo_aprobado",
		"saldo_usado",
		"saldo_disponible",
		"estado",
		"creado_en",
	)
	list_filter = ("estado", "creado_en")
	search_fields = (
		"maestro__usuario__email",
		"maestro__rut",
		"maestro__rubro",
	)


@admin.register(MovimientoCredito)
class MovimientoCreditoAdmin(admin.ModelAdmin):
	list_display = ("cuenta", "tipo", "monto", "descripcion", "creado_en")
	list_filter = ("tipo", "creado_en")
	search_fields = (
		"cuenta__maestro__usuario__email",
		"cuenta__maestro__rut",
		"descripcion",
	)


@admin.register(CuotaCredito)
class CuotaCreditoAdmin(admin.ModelAdmin):
	list_display = (
		"cuenta",
		"numero_cuota",
		"total_cuotas",
		"monto",
		"fecha_vencimiento",
		"estado",
	)
	list_filter = ("estado", "fecha_vencimiento", "creado_en")
	search_fields = (
		"cuenta__maestro__usuario__email",
		"cuenta__maestro__rut",
	)
