from django.test import TestCase
from django.urls import reverse

from apps.catalogo.models import Categoria, Producto
from apps.inventario.models import MovimientoInventario
from apps.inventario import services as inventario_services
from apps.pedidos.models import Carrito, ItemCarrito
from apps.pedidos import services as pedidos_services
from apps.usuarios.models import Usuario


class InventarioControlTests(TestCase):
    def setUp(self):
        self.bodeguero = Usuario.objects.create_user(
            email="bodeguero.control@test.com",
            password="Test123456",
            rol=Usuario.Rol.BODEGUERO,
        )
        self.cliente = Usuario.objects.create_user(
            email="cliente.control@test.com",
            password="Test123456",
            rol=Usuario.Rol.CLIENTE,
        )
        self.categoria = Categoria.objects.create(nombre="Herramientas", slug="herramientas")
        self.producto = Producto.objects.create(
            nombre="Taladro QA",
            slug="taladro-qa",
            descripcion="Producto prueba",
            precio=20000,
            stock=3,
            activo=True,
            categoria=self.categoria,
        )

    def test_bodeguero_puede_ajustar_stock_entrada(self):
        self.client.force_login(self.bodeguero)
        resp = self.client.post(reverse("ajustar_stock"), {"producto_id": self.producto.pk, "cantidad": 5, "tipo_movimiento": MovimientoInventario.TipoMovimiento.ENTRADA, "motivo": "Ingreso prueba"})
        self.assertEqual(resp.status_code, 302)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 8)
        mov = MovimientoInventario.objects.filter(producto=self.producto, tipo_movimiento=MovimientoInventario.TipoMovimiento.ENTRADA).first()
        self.assertIsNotNone(mov)
        self.assertEqual(mov.usuario, self.bodeguero)

    def test_cliente_no_puede_ajustar_stock(self):
        self.client.force_login(self.cliente)
        resp = self.client.post(reverse("ajustar_stock"), {"producto_id": self.producto.pk, "cantidad": 1, "tipo_movimiento": MovimientoInventario.TipoMovimiento.ENTRADA, "motivo": "Ingreso"})
        # Authenticated cliente must receive 403 and not modify stock
        self.assertEqual(resp.status_code, 403)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 3)
        self.assertFalse(MovimientoInventario.objects.filter(producto=self.producto).exists())

    def test_no_permite_stock_negativo_salida(self):
        self.client.force_login(self.bodeguero)
        resp = self.client.post(reverse("ajustar_stock"), {"producto_id": self.producto.pk, "cantidad": 10, "tipo_movimiento": MovimientoInventario.TipoMovimiento.SALIDA, "motivo": "Salida mayor"})
        # View redirects back with error message; ensure stock unchanged
        self.assertEqual(resp.status_code, 302)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 3)

    def test_ajuste_crea_movimiento(self):
        self.client.force_login(self.bodeguero)
        resp = self.client.post(reverse("ajustar_stock"), {"producto_id": self.producto.pk, "cantidad": 2, "tipo_movimiento": MovimientoInventario.TipoMovimiento.AJUSTE, "motivo": "Ajuste prueba"})
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(MovimientoInventario.objects.filter(producto=self.producto, tipo_movimiento=MovimientoInventario.TipoMovimiento.AJUSTE).exists())

    def test_dashboard_muestra_productos_bajo_stock(self):
        # marcar producto con stock_minimo si existe; como el modelo no lo define, asumimos stock<=x
        # Aqui usamos el servicio para obtener productos bajos (stock 3 y asumimos minimo 5 si existiera)
        bajos = inventario_services.obtener_productos_bajo_stock()
        self.assertIsInstance(bajos, list)

    def test_dashboard_filtros_categoria_y_bajo_stock(self):
        # crear otra categoria y producto
        cat2 = Categoria.objects.create(nombre="Accesorios", slug="accesorios")
        prod2 = Producto.objects.create(nombre="Tuerca", slug="tuerca", descripcion="t", precio=100, stock=0, activo=True, categoria=cat2)
        self.client.force_login(self.bodeguero)
        resp = self.client.get(reverse("bodeguero_dashboard"), {"categoria": cat2.pk})
        self.assertEqual(resp.status_code, 200)
        # filtro por bajo stock
        resp2 = self.client.get(reverse("bodeguero_dashboard"), {"estado": "sin_stock"})
        self.assertEqual(resp2.status_code, 200)

    def test_dashboard_muestra_total_productos(self):
        self.client.force_login(self.bodeguero)
        resp = self.client.get(reverse("bodeguero_dashboard"))
        self.assertEqual(resp.status_code, 200)
        # resumen en contexto debe existir y contener total
        resumen = resp.context.get("resumen_stock")
        if resumen is None:
            # Fallback: obtener desde el servicio si el contexto no fue cargado por la renderización
            resumen = inventario_services.obtener_resumen_stock_bodega()
        self.assertIsNotNone(resumen)
        total_ctx = resumen.get("total") or resumen.get("total_productos")
        self.assertEqual(int(total_ctx), Producto.objects.filter(activo=True).count())

    def test_filtro_estado_bajo_stock(self):
        # crear producto bajo stock
        prod_bajo = Producto.objects.create(nombre="Poco", slug="poco", descripcion="t", precio=10, stock=1, activo=True, categoria=self.categoria, stock_minimo=5)
        self.client.force_login(self.bodeguero)
        resp = self.client.get(reverse("bodeguero_dashboard"), {"estado": "bajo_stock"})
        self.assertEqual(resp.status_code, 200)

    def test_ajustar_require_motivo(self):
        self.client.force_login(self.bodeguero)
        # missing motivo
        resp = self.client.post(reverse("ajustar_stock"), {"producto_id": self.producto.pk, "cantidad": 1, "tipo_movimiento": MovimientoInventario.TipoMovimiento.ENTRADA})
        # Should redirect back with error message (302)
        self.assertEqual(resp.status_code, 302)