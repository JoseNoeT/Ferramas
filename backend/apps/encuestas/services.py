from django.db import transaction
from django.db.models import Avg, Count

from apps.encuestas.models import EncuestaSatisfaccion


@transaction.atomic
def crear_encuesta_satisfaccion(cliente, pedido, datos):
	if pedido.usuario_id != cliente.id:
		raise ValueError("No puedes responder encuestas de pedidos ajenos.")

	if hasattr(pedido, "encuesta_satisfaccion"):
		raise ValueError("Ya respondiste esta encuesta.")

	try:
		calificacion = int(datos.get("calificacion"))
	except (TypeError, ValueError):
		raise ValueError("La calificacion debe ser un numero entre 1 y 5.")

	if calificacion < 1 or calificacion > 5:
		raise ValueError("La calificacion debe estar entre 1 y 5.")

	comentario = (datos.get("comentario") or "").strip()

	return EncuestaSatisfaccion.objects.create(
		pedido=pedido,
		cliente=cliente,
		calificacion=calificacion,
		comentario=comentario,
	)


def obtener_resumen_encuestas():
	queryset = EncuestaSatisfaccion.objects.select_related("pedido", "cliente")
	total_encuestas = queryset.count()
	promedio = queryset.aggregate(prom=Avg("calificacion"))["prom"]

	total_por_calificacion_qs = queryset.values("calificacion").annotate(total=Count("id"))
	total_por_calificacion = {str(i): 0 for i in range(1, 6)}
	for fila in total_por_calificacion_qs:
		total_por_calificacion[str(fila["calificacion"])] = fila["total"]

	ultimas_encuestas = list(queryset.order_by("-creado_en")[:20])

	return {
		"total_encuestas": total_encuestas,
		"promedio_calificacion": round(float(promedio), 2) if promedio is not None else 0,
		"total_por_calificacion": total_por_calificacion,
		"ultimas_encuestas": ultimas_encuestas,
	}
