"""URL routes for usuarios app."""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.home_view, name="home"),
    path("login/", views.login_view, name="login"),
    path("registro/", views.registro_view, name="registro"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/admin/", views.admin_dashboard_view, name="admin_dashboard"),
    path(
        "dashboard/admin/usuarios/",
        views.admin_usuarios_dashboard_view,
        name="admin_usuarios_dashboard",
    ),
    path(
        "dashboard/admin/usuarios/crear/",
        views.crear_usuario_interno_view,
        name="admin_usuario_crear",
    ),
    path(
        "dashboard/admin/usuarios/<int:pk>/editar/",
        views.editar_usuario_interno_view,
        name="admin_usuario_editar",
    ),
    path(
        "dashboard/admin/usuarios/<int:pk>/estado/",
        views.cambiar_estado_usuario_view,
        name="admin_usuario_estado",
    ),
    path("dashboard/contador/", views.contador_dashboard_view, name="contador_dashboard"),
]

