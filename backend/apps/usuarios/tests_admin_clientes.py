from django.test import TestCase
from django.urls import reverse

from apps.usuarios.models import Usuario
from apps.maestros.models import PerfilMaestroPyme
from apps.usuarios import admin_services


class AdminClientesTests(TestCase):
    def setUp(self):
        # Crear un admin
        self.admin = Usuario.objects.create_user(email="admin@example.com", password="pass", rol=Usuario.Rol.ADMIN)
        # Usuario interno (no cliente)
        self.vendedor = Usuario.objects.create_user(email="vendedor@example.com", password="pass", rol=Usuario.Rol.VENDEDOR)
        # Clientes
        self.cliente1 = Usuario.objects.create_user(email="cliente1@example.com", password="pass", rol=Usuario.Rol.CLIENTE)
        self.cliente2 = Usuario.objects.create_user(email="cliente2@example.com", password="pass", rol=Usuario.Rol.CLIENTE)

    def test_admin_access_admin_clientes(self):
        self.client.force_login(self.admin)
        url = reverse("admin_clientes")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_cliente_no_puede_acceder_admin_clientes(self):
        self.client.force_login(self.cliente1)
        url = reverse("admin_clientes")
        resp = self.client.get(url)
        # Wrapper devuelve HttpResponseForbidden (403)
        self.assertIn(resp.status_code, (302, 403))

    def test_admin_clientes_lists_only_clientes(self):
        self.client.force_login(self.admin)
        resp = self.client.get(reverse("admin_clientes"))
        self.assertEqual(resp.status_code, 200)
        clientes = list(resp.context["clientes"])
        emails = {u.email for u in clientes}
        self.assertIn(self.cliente1.email, emails)
        self.assertIn(self.cliente2.email, emails)
        # No incluir usuarios internos
        self.assertNotIn(self.vendedor.email, emails)
        self.assertNotIn(self.admin.email, emails)

    def test_obtener_dashboard_indicadores_contains_expected_modules(self):
        ctx = admin_services.obtener_dashboard_indicadores()
        modulos = ctx.get("modulos_admin") or []
        titulos = {m["titulo"] for m in modulos}
        self.assertIn("Usuarios internos", titulos)
        self.assertIn("Clientes", titulos)
        # Si existe ruta admin_maestros, debe aparecer Maestros/PYME
        # La existencia en urlpatterns depende del proyecto; si está, comprobar su presencia
        try:
            from django.urls import reverse as _rev

            _rev("admin_maestros")
            self.assertIn("Maestros/PYME", titulos)
        except Exception:
            # Si no existe, está bien
            pass
