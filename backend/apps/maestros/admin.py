from django.contrib import admin

from apps.maestros.models import PerfilMaestroPyme, ServicioMaestro, SolicitudAsesoria


@admin.register(PerfilMaestroPyme)
class PerfilMaestroPymeAdmin(admin.ModelAdmin):
	list_display = (
		"usuario",
		"tipo",
		"rut",
		"rubro",
		"estado",
		"descuento_primera_compra_usado",
		"creado_en",
	)
	list_filter = ("tipo", "estado", "descuento_primera_compra_usado", "creado_en")
	search_fields = ("usuario__email", "rut", "rubro", "oficio", "nombre_empresa")


@admin.register(ServicioMaestro)
class ServicioMaestroAdmin(admin.ModelAdmin):
	list_display = ("titulo", "maestro", "rubro", "zona_atencion", "activo", "creado_en")
	list_filter = ("activo", "rubro", "creado_en")
	search_fields = ("titulo", "descripcion", "rubro", "zona_atencion", "maestro__usuario__email")


@admin.register(SolicitudAsesoria)
class SolicitudAsesoriaAdmin(admin.ModelAdmin):
	list_display = (
		"nombre_cliente",
		"email_cliente",
		"telefono_cliente",
		"servicio",
		"estado",
		"cargo_confirmacion",
		"creado_en",
	)
	list_filter = ("estado", "creado_en")
	search_fields = (
		"nombre_cliente",
		"email_cliente",
		"telefono_cliente",
		"direccion_o_comuna",
		"servicio__titulo",
		"cliente__email",
	)
