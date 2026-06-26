from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch

from apps.catalogo.models import Categoria, Producto
from apps.pedidos.models import Carrito, ItemCarrito, Pedido
from apps.pagos.models import Pago
from apps.usuarios.models import Usuario


class CheckoutAdvancedTests(TestCase):
    def setUp(self):
        self.user_password = "Test123456"
        self.user = Usuario.objects.create_user(
            email="cliente.adv@test.com", password=self.user_password, rol=Usuario.Rol.CLIENTE
        )
        self.categoria = Categoria.objects.create(nombre="Herramientas", slug="herramientas-adv")
        self.producto = Producto.objects.create(
            nombre="Taladro QA",
            slug="taladro-qa",
            descripcion="Producto prueba advanced checkout",
            precio=20000,
            stock=10,
            activo=True,
            categoria=self.categoria,
        )

    def _create_carrito_item(self, cantidad=1):
        carrito = Carrito.objects.create(usuario=self.user)
        ItemCarrito.objects.create(carrito=carrito, producto=self.producto, cantidad=cantidad)
        return carrito

    def test_checkout_webpay_crea_pedido_y_redirige_sin_duplicar(self):
        # Ruta real de checkout: name="checkout"
        self._create_carrito_item(cantidad=2)
        self.client.force_login(self.user)

        resp = self.client.post(
            reverse("checkout"),
            {"medio_pago": Pago.MedioPago.WEBPAY, "tipo_entrega": Pedido.TipoEntrega.RETIRO},
        )

        # Debe redirigir al flujo Webpay (namespaced 'pagos:webpay_iniciar')
        self.assertEqual(resp.status_code, 302)
        # Debe existir exactamente 1 pedido para el usuario
        self.assertEqual(Pedido.objects.filter(usuario=self.user).count(), 1)
        pedido = Pedido.objects.filter(usuario=self.user).first()
        expected = reverse("pagos:webpay_iniciar", kwargs={"pedido_id": pedido.pk})
        self.assertIn(expected, resp["Location"])

    def test_checkout_con_puntos_llama_aplicar_y_acumular(self):
        carrito = self._create_carrito_item(cantidad=1)
        self.client.force_login(self.user)

        # Parchear funciones de puntos que se usan en views (importadas como puntos_services)
        with patch("apps.pedidos.views.puntos_services.aplicar_puntos") as mock_aplicar, patch(
            "apps.pedidos.views.puntos_services.acumular_puntos_por_pedido"
        ) as mock_acumular:
            resp = self.client.post(
                reverse("checkout"),
                {"medio_pago": Pago.MedioPago.TIENDA, "tipo_entrega": Pedido.TipoEntrega.RETIRO, "puntos_a_usar": "50"},
            )

            # Flujo no-webpay debe redirigir a confirmacion
            self.assertEqual(resp.status_code, 302)
            # Se debe haber llamado a aplicar_puntos y acumular_puntos_por_pedido
            self.assertTrue(mock_aplicar.called, "aplicar_puntos no fue llamado")
            self.assertTrue(mock_acumular.called, "acumular_puntos_por_pedido no fue llamado")

    def test_cliente_normal_no_puede_usar_ferrecredito(self):
        # Cliente sin perfil Maestro/PYME intenta usar ferrecredito
        self._create_carrito_item(cantidad=1)
        self.client.force_login(self.user)

        # Parchear validar_uso_ferrecredito para simular rechazo (lanza ValueError)
        with patch("apps.pedidos.views.credito_services.validar_uso_ferrecredito") as mock_validar, patch(
            "apps.pedidos.views.pagos_services.registrar_pago_ferrecredito"
        ) as mock_registrar:
            mock_validar.side_effect = ValueError("No autorizado para FerreCrédito")

            resp = self.client.post(
                reverse("checkout"),
                {"medio_pago": Pago.MedioPago.FERRECREDITO, "tipo_entrega": Pedido.TipoEntrega.RETIRO},
            )

            # checkout_view captura ValueError y re-renderiza checkout (status 200)
            self.assertEqual(resp.status_code, 200)
            # No se debe haber registrado pago FerreCrédito
            self.assertEqual(
                Pago.objects.filter(medio_pago=Pago.MedioPago.FERRECREDITO).count(), 0
            )
            self.assertFalse(mock_registrar.called, "registrar_pago_ferrecredito fue llamado inesperadamente")
