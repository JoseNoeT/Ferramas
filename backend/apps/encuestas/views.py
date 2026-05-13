from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import redirect, render
from apps.encuestas import services as encuestas_services
from apps.pedidos.models import Pedido
from apps.usuarios.views import _requiere_admin
from rest_framework import viewsets


class VistaPlaceholder(viewsets.ViewSet):
    """ViewSet temporal de la app encuestas."""

    # TODO: Reemplazar por ViewSets reales por recurso.
    pass


def encuesta_satisfaccion_view(request):
    messages.info(
        request,
        "Debes responder la encuesta desde un pedido confirmado.",
    )
    return render(
        request,
        "pages/encuesta-satisfaccion.html",
        {
            "pedido": None,
            "encuesta_existente": None,
        },
    )


@login_required
def encuesta_satisfaccion_pedido_view(request, pedido_id):
    try:
        pedido = Pedido.objects.get(pk=pedido_id, usuario=request.user)
    except Pedido.DoesNotExist:
        raise Http404("Pedido no encontrado.")

    encuesta_existente = getattr(pedido, "encuesta_satisfaccion", None)
    if encuesta_existente:
        messages.info(request, "Ya respondiste esta encuesta.")
        return render(
            request,
            "pages/encuesta-satisfaccion.html",
            {
                "pedido": pedido,
                "encuesta_existente": encuesta_existente,
            },
        )

    if request.method == "POST":
        try:
            encuestas_services.crear_encuesta_satisfaccion(request.user, pedido, request.POST)
            messages.success(request, "Encuesta enviada correctamente. Gracias por tu feedback.")
            return redirect("confirmacion", pk=pedido.pk)
        except ValueError as exc:
            messages.error(request, str(exc))

    return render(
        request,
        "pages/encuesta-satisfaccion.html",
        {
            "pedido": pedido,
            "encuesta_existente": None,
        },
    )


@_requiere_admin
def admin_encuestas_view(request):
    resumen = encuestas_services.obtener_resumen_encuestas()
    total_por_calificacion = resumen.get("total_por_calificacion", {})
    resumen["calificacion_1"] = total_por_calificacion.get("1", 0)
    resumen["calificacion_2"] = total_por_calificacion.get("2", 0)
    resumen["calificacion_3"] = total_por_calificacion.get("3", 0)
    resumen["calificacion_4"] = total_por_calificacion.get("4", 0)
    resumen["calificacion_5"] = total_por_calificacion.get("5", 0)
    return render(request, "dashboard/admin-encuestas.html", resumen)

