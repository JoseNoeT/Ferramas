from django.test import TestCase
from django.utils import timezone
from datetime import timedelta

from apps.catalogo.forms import ProductoForm
from apps.catalogo.models import Producto, Categoria
from apps.usuarios.models import Usuario
from django.urls import reverse


class OfertasTests(TestCase):
    def setUp(self):
        self.admin = Usuario.objects.create_user(email="admin@test.com", password="Test123456", rol=Usuario.Rol.ADMIN)
        self.cliente = Usuario.objects.create_user(email="cli@test.com", password="Test123456", rol=Usuario.Rol.CLIENTE)
        self.categoria = Categoria.objects.create(nombre="Herramientas", slug="herr")

    def test_oferta_valida_guarda(self):
        now = timezone.now()
        data = {
            "nombre": "Taladro",
            "slug": "taladro-test",
            "descripcion": "t",
            "precio": 10000,
            "en_oferta": True,
            "precio_oferta": 8000,
            "fecha_inicio_oferta": now - timedelta(days=1),
            "fecha_fin_oferta": now + timedelta(days=5),
            "stock": 10,
            "activo": True,
            "categoria": self.categoria.pk,
        }
        form = ProductoForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)
        producto = form.save()
        self.assertTrue(producto.en_oferta)

    def test_precio_oferta_mayor_o_igual_precio_falla(self):
        now = timezone.now()
        data = {
            "nombre": "Taladro2",
            "slug": "taladro2",
            "descripcion": "t",
            "precio": 10000,
            "en_oferta": True,
            "precio_oferta": 12000,
            "fecha_inicio_oferta": now - timedelta(days=1),
            "fecha_fin_oferta": now + timedelta(days=5),
            "stock": 10,
            "activo": True,
            "categoria": self.categoria.pk,
        }
        form = ProductoForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("precio_oferta", form.errors)

    def test_fechas_invalidas_fallan(self):
        now = timezone.now()
        data = {
            "nombre": "Taladro3",
            "slug": "taladro3",
            "descripcion": "t",
            "precio": 10000,
            "en_oferta": True,
            "precio_oferta": 8000,
            "fecha_inicio_oferta": now + timedelta(days=5),
            "fecha_fin_oferta": now + timedelta(days=1),
            "stock": 10,
            "activo": True,
            "categoria": self.categoria.pk,
        }
        form = ProductoForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("fecha_fin_oferta", form.errors)

    def test_producto_en_oferta_vigente_aparece_en_ofertas(self):
        now = timezone.now()
        p = Producto.objects.create(
            nombre="ProdOn",
            slug="prodon",
            descripcion="t",
            precio=10000,
            stock=5,
            activo=True,
            categoria=self.categoria,
            en_oferta=True,
            precio_oferta=8000,
            fecha_inicio_oferta=now - timedelta(days=1),
            fecha_fin_oferta=now + timedelta(days=1),
        )
        resp = self.client.get(reverse("ofertas"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, p.nombre)

    def test_producto_vencido_no_aparece_en_ofertas(self):
        now = timezone.now()
        p = Producto.objects.create(
            nombre="ProdOld",
            slug="prodold",
            descripcion="t",
            precio=10000,
            stock=5,
            activo=True,
            categoria=self.categoria,
            en_oferta=True,
            precio_oferta=8000,
            fecha_inicio_oferta=now - timedelta(days=10),
            fecha_fin_oferta=now - timedelta(days=5),
        )
        resp = self.client.get(reverse("ofertas"))
        self.assertEqual(resp.status_code, 200)
        self.assertNotContains(resp, p.nombre)

    def test_cliente_no_admin_no_gestiona_ofertas(self):
        # cliente intenta acceder a crear producto (panel admin)
        self.client.force_login(self.cliente)
        resp = self.client.get(reverse("admin_productos_dashboard"))
        self.assertEqual(resp.status_code, 403)
# Tests para la app catalogo
from django.test import TestCase
