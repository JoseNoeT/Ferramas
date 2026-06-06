from django.urls import path

from apps.pedidos import views

urlpatterns = [
    # ── Flujo cliente ──────────────────────────────────────────────────────────
    path("carrito/", views.carrito_view, name="carrito"),
    path("carrito/agregar/", views.agregar_al_carrito_view, name="agregar_al_carrito"),
    path("carrito/actualizar/", views.actualizar_item_carrito_view, name="actualizar_item_carrito"),
    path("carrito/eliminar/", views.eliminar_item_carrito_view, name="eliminar_item_carrito"),
    path("checkout/", views.checkout_view, name="checkout"),
    path("pedido/<int:pk>/", views.pedido_confirmacion_view, name="confirmacion"),

    # ── Dashboard Vendedor ─────────────────────────────────────────────────────
    path("dashboard/vendedor/", views.vendedor_dashboard_view, name="vendedor_dashboard"),
    path("pedido/<int:pk>/aprobar/", views.aprobar_pedido_view, name="aprobar_pedido"),
    path("pedido/<int:pk>/rechazar/", views.rechazar_pedido_view, name="rechazar_pedido"),
    path("pedido/<int:pk>/enviar-bodega/", views.enviar_a_bodega_view, name="enviar_a_bodega"),

    # ── Dashboard Bodeguero ────────────────────────────────────────────────────
    path("dashboard/bodeguero/", views.bodeguero_dashboard_view, name="bodeguero_dashboard"),
    path("pedido/<int:pk>/en-preparacion/", views.poner_en_preparacion_view, name="pedido_en_preparacion"),
    path("pedido/<int:pk>/marcar-listo/", views.marcar_pedido_listo_view, name="pedido_marcar_listo"),
    path("pedido/<int:pk>/entregado/", views.pedido_entregado_view, name="pedido_entregado"),
]
