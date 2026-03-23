from django.urls import path

from apps.catalogo import views

urlpatterns = [
    path("catalogo/", views.catalogo_view, name="catalogo"),
    path("catalogo/<slug:slug>/", views.producto_detalle_view, name="producto_detalle"),
    path(
        "dashboard/admin/productos/",
        views.admin_productos_dashboard_view,
        name="admin_productos_dashboard",
    ),
    path(
        "dashboard/admin/productos/crear/",
        views.crear_producto_view,
        name="admin_producto_crear",
    ),
    path(
        "dashboard/admin/productos/<int:pk>/editar/",
        views.editar_producto_view,
        name="admin_producto_editar",
    ),
    path(
        "dashboard/admin/productos/<int:pk>/estado/",
        views.cambiar_estado_producto_view,
        name="admin_producto_estado",
    ),
    path(
        "dashboard/admin/categorias/",
        views.admin_categorias_dashboard_view,
        name="admin_categorias_dashboard",
    ),
]
