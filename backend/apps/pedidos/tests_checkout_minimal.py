from django.test import TestCase

from rest_framework.test import APIClient

from apps.catalogo.models import Categoria, Producto
from apps.pedidos import services as pedidos_services
from apps.pedidos.models import Carrito, ItemCarrito, Pedido
from apps.usuarios.models import Usuario


class CheckoutMinimalTests(TestCase):
    def setUp(self):
        self.usuario_password = "Test123456"
        self.usuario = Usuario.objects.create_user(
            email="cliente.checkout@test.com",
            password=self.usuario_password,
            rol=Usuario.Rol.CLIENTE,
        )
        self.categoria = Categoria.objects.create(nombre="Herramientas", slug="herramientas-test")
        self.producto = Producto.objects.create(
            nombre="Destornillador QA",
            slug="destornillador-qa",
            descripcion="Producto prueba checkout",
            precio=10000,
            stock=10,
            activo=True,
            categoria=self.categoria,
        )

    def test_agregar_producto_al_carrito(self):
        item = pedidos_services.agregar_producto_al_carrito(self.usuario, self.producto.pk, 2)
        carrito = Carrito.objects.get(usuario=self.usuario)
        self.assertIsNotNone(item)
        self.assertEqual(item.cantidad, 2)
        self.assertEqual(item.producto.pk, self.producto.pk)
        self.assertEqual(carrito.items.count(), 1)

    def test_crear_pedido_desde_carrito(self):
        carrito = Carrito.objects.create(usuario=self.usuario)
        ItemCarrito.objects.create(carrito=carrito, producto=self.producto, cantidad=3)

        pedido = pedidos_services.crear_pedido_desde_carrito(self.usuario, Pedido.TipoEntrega.RETIRO)

        pedido.refresh_from_db()
        self.producto.refresh_from_db()
        self.assertEqual(Pedido.objects.filter(usuario=self.usuario).count(), 1)
        self.assertEqual(pedido.items.count(), 1)
        self.assertEqual(pedido.subtotal, self.producto.precio * 3)
        carrito.refresh_from_db()
        self.assertEqual(carrito.items.count(), 0)
        # comportamiento actual: inventario reserva/descuenta stock
        self.assertEqual(self.producto.stock, 7)

    def test_carrito_vacio_no_crea_pedido(self):
        Carrito.objects.create(usuario=self.usuario)
        with self.assertRaises(ValueError):
            pedidos_services.crear_pedido_desde_carrito(self.usuario, Pedido.TipoEntrega.RETIRO)

    def test_stock_insuficiente_no_crea_pedido(self):
        carrito = Carrito.objects.create(usuario=self.usuario)
        ItemCarrito.objects.create(carrito=carrito, producto=self.producto, cantidad=99)
        with self.assertRaises(ValueError):
            pedidos_services.crear_pedido_desde_carrito(self.usuario, Pedido.TipoEntrega.RETIRO)

    def test_api_post_create_pedido_from_carrito(self):
        # Crear carrito y item
        carrito = Carrito.objects.create(usuario=self.usuario)
        ItemCarrito.objects.create(carrito=carrito, producto=self.producto, cantidad=2)

        client = APIClient()
        # Obtener token JWT desde el endpoint real
        token_resp = client.post("/api/autenticacion/token/", {"email": self.usuario.email, "password": self.usuario_password}, format="json")
        self.assertEqual(token_resp.status_code, 200)
        access = token_resp.json().get("access")
        self.assertIsNotNone(access)

        client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        resp = client.post("/api/pedidos/create/", {"tipo_entrega": Pedido.TipoEntrega.RETIRO}, format="json")
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        self.assertIn("id", data)

        pedido = Pedido.objects.get(pk=data["id"])
        carrito.refresh_from_db()
        self.assertEqual(carrito.items.count(), 0)
        self.assertEqual(pedido.items.count(), 1)
