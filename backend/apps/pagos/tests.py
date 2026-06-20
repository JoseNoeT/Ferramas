from unittest.mock import patch

from django.test import TestCase

from apps.pagos import services as pagos_services
from apps.pagos.models import Pago
from apps.pedidos.models import Pedido, ItemPedido
from apps.usuarios.models import Usuario
from apps.catalogo.models import Producto, Categoria
from apps.inventario import services as inventario_services
from apps.inventario.models import MovimientoInventario


class PagosServicesTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            email="cliente.pagos@test.com",
            password="Test123456",
            rol=Usuario.Rol.CLIENTE,
        )
        self.pedido = Pedido.objects.create(
            usuario=self.usuario,
            estado=Pedido.Estado.GENERADO,
            subtotal=25000,
            total=25000,
            total_final=25000,
        )

    def test_registrar_pago_pendiente_tienda_crea_pago_y_mantiene_pendiente(self):
        pago = pagos_services.registrar_pago_pendiente_tienda(self.pedido, usuario=self.usuario)

        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.payment_status, Pedido.PaymentStatus.PENDIENTE)
        self.assertEqual(pago.medio_pago, Pago.MedioPago.TIENDA)
        self.assertEqual(pago.estado, Pago.Estado.INICIADO)

    @patch("apps.pagos.services.puntos_services.acumular_puntos_por_pedido")
    @patch("apps.pagos.services._get_transaction_client")
    def test_confirmar_webpay_response_code_cero_actualiza_pagado(self, mock_client_factory, _mock_puntos):
        pago = Pago.objects.create(
            pedido=self.pedido,
            medio_pago=Pago.MedioPago.WEBPAY,
            monto=self.pedido.total_final,
            estado=Pago.Estado.REDIRIGIDO,
            buy_order="PED-TEST-001",
            session_id="SES-TEST-001",
            token_ws="TOKEN-TEST-001",
            url_webpay="https://webpay3gint.transbank.cl",
        )

        client = mock_client_factory.return_value
        client.commit.return_value = {
            "response_code": 0,
            "authorization_code": "AUTH123",
            "transaction_date": "2026-06-06T12:00:00+00:00",
        }

        pago_actualizado = pagos_services.confirmar_transaccion_webpay("TOKEN-TEST-001")

        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.payment_status, Pedido.PaymentStatus.PAGADO)
        self.assertEqual(pago_actualizado.pk, pago.pk)
        self.assertEqual(pago_actualizado.estado, Pago.Estado.AUTORIZADO)

    def test_obtener_pagos_por_medio_para_contador(self):
        pedido_tienda = Pedido.objects.create(
            usuario=self.usuario,
            estado=Pedido.Estado.GENERADO,
            subtotal=12000,
            total=12000,
            total_final=12000,
        )
        pagos_services.registrar_pago_pendiente_tienda(pedido_tienda, usuario=self.usuario)

        pedido_credito = Pedido.objects.create(
            usuario=self.usuario,
            estado=Pedido.Estado.GENERADO,
            subtotal=18000,
            total=18000,
            total_final=18000,
        )
        pagos_services.marcar_pedido_pagado(
            pedido_credito,
            medio_pago=Pago.MedioPago.FERRECREDITO,
            referencia="FERRECREDITO-TEST",
        )

        pedido_webpay = Pedido.objects.create(
            usuario=self.usuario,
            estado=Pedido.Estado.GENERADO,
            subtotal=10000,
            total=10000,
            total_final=10000,
        )
        Pago.objects.create(
            pedido=pedido_webpay,
            medio_pago=Pago.MedioPago.WEBPAY,
            monto=pedido_webpay.total_final,
            estado=Pago.Estado.AUTORIZADO,
            buy_order="PED-WEBPAY-TEST",
            session_id="SES-WEBPAY-TEST",
            token_ws="TOKEN-WEBPAY-TEST",
            url_webpay="https://webpay3gint.transbank.cl",
        )

        pagos_webpay = pagos_services.obtener_pagos_webpay()
        pagos_ferrecredito = pagos_services.obtener_pagos_ferrecredito()
        pagos_tienda_pendientes = pagos_services.obtener_pagos_tienda_pendientes()

        self.assertTrue(pagos_webpay.filter(medio_pago=Pago.MedioPago.WEBPAY).exists())
        self.assertTrue(
            pagos_ferrecredito.filter(medio_pago=Pago.MedioPago.FERRECREDITO).exists()
        )
        self.assertTrue(
            pagos_tienda_pendientes.filter(medio_pago=Pago.MedioPago.TIENDA).exists()
        )

    @patch("apps.pagos.services.puntos_services.acumular_puntos_por_pedido")
    @patch("apps.pagos.services._get_transaction_client")
    def test_confirmar_webpay_descuenta_stock_y_marca_descontado(self, mock_client_factory, _mock_puntos):
        # crear producto y item en el pedido
        categoria = Categoria.objects.create(nombre="Cat", slug="cat")
        producto = Producto.objects.create(nombre="Martillo", slug="martillo", descripcion="t", precio=1000, stock=10, activo=True, categoria=categoria)
        ItemPedido.objects.create(pedido=self.pedido, tipo_linea="producto", producto=producto, cantidad=3, precio_unitario=1000)

        pago = Pago.objects.create(
            pedido=self.pedido,
            medio_pago=Pago.MedioPago.WEBPAY,
            monto=self.pedido.total_final,
            estado=Pago.Estado.REDIRIGIDO,
            buy_order="PED-TEST-002",
            session_id="SES-TEST-002",
            token_ws="TOKEN-TEST-002",
            url_webpay="https://webpay3gint.transbank.cl",
        )

        client = mock_client_factory.return_value
        client.commit.return_value = {
            "response_code": 0,
            "authorization_code": "AUTH124",
            "transaction_date": "2026-06-06T12:00:00+00:00",
        }

        pago_actualizado = pagos_services.confirmar_transaccion_webpay("TOKEN-TEST-002")

        producto.refresh_from_db()
        self.pedido.refresh_from_db()

        self.assertEqual(self.pedido.payment_status, Pedido.PaymentStatus.PAGADO)
        self.assertEqual(producto.stock, 7)
        self.assertTrue(self.pedido.stock_descontado)
        # movimiento SALIDA creado
        self.assertTrue(MovimientoInventario.objects.filter(pedido=self.pedido, producto=producto, tipo_movimiento=MovimientoInventario.TipoMovimiento.SALIDA).exists())

    @patch("apps.pagos.services.puntos_services.acumular_puntos_por_pedido")
    @patch("apps.pagos.services._get_transaction_client")
    def test_confirmar_webpay_con_reserva_no_descuenta_de_nuevo(self, mock_client_factory, _mock_puntos):
        categoria = Categoria.objects.create(nombre="Cat2", slug="cat2")
        producto = Producto.objects.create(nombre="Destornillador", slug="dest", descripcion="t", precio=500, stock=10, activo=True, categoria=categoria)
        ItemPedido.objects.create(pedido=self.pedido, tipo_linea="producto", producto=producto, cantidad=3, precio_unitario=500)

        # Reservar stock previamente (flujo normal al crear pedido)
        inventario_services.reservar_stock_pedido(self.pedido, usuario=self.usuario)
        producto.refresh_from_db()

        self.assertEqual(producto.stock, 7)

        pago = Pago.objects.create(
            pedido=self.pedido,
            medio_pago=Pago.MedioPago.WEBPAY,
            monto=self.pedido.total_final,
            estado=Pago.Estado.REDIRIGIDO,
            buy_order="PED-TEST-003",
            session_id="SES-TEST-003",
            token_ws="TOKEN-TEST-003",
            url_webpay="https://webpay3gint.transbank.cl",
        )

        client = mock_client_factory.return_value
        client.commit.return_value = {"response_code": 0, "authorization_code": "AUTH125", "transaction_date": "2026-06-06T12:00:00+00:00"}

        pagos_services.confirmar_transaccion_webpay("TOKEN-TEST-003")

        producto.refresh_from_db()
        self.pedido.refresh_from_db()

        # No debe descontar doble: stock permanece igual (7), y se marca stock_descontado
        self.assertEqual(producto.stock, 7)
        self.assertTrue(self.pedido.stock_reservado)
        self.assertTrue(self.pedido.stock_descontado)

    @patch("apps.pagos.services.puntos_services.acumular_puntos_por_pedido")
    @patch("apps.pagos.services._get_transaction_client")
    def test_confirmar_webpay_idempotente_al_confirmar_dos_veces(self, mock_client_factory, _mock_puntos):
        categoria = Categoria.objects.create(nombre="Cat3", slug="cat3")
        producto = Producto.objects.create(nombre="Llave", slug="llave", descripcion="t", precio=800, stock=10, activo=True, categoria=categoria)
        ItemPedido.objects.create(pedido=self.pedido, tipo_linea="producto", producto=producto, cantidad=2, precio_unitario=800)

        pago = Pago.objects.create(
            pedido=self.pedido,
            medio_pago=Pago.MedioPago.WEBPAY,
            monto=self.pedido.total_final,
            estado=Pago.Estado.REDIRIGIDO,
            buy_order="PED-TEST-004",
            session_id="SES-TEST-004",
            token_ws="TOKEN-TEST-004",
            url_webpay="https://webpay3gint.transbank.cl",
        )

        client = mock_client_factory.return_value
        client.commit.return_value = {"response_code": 0, "authorization_code": "AUTH126", "transaction_date": "2026-06-06T12:00:00+00:00"}

        pagos_services.confirmar_transaccion_webpay("TOKEN-TEST-004")
        producto.refresh_from_db()
        self.assertEqual(producto.stock, 8)

        # Confirmar de nuevo (debe ser idempotente)
        pagos_services.confirmar_transaccion_webpay("TOKEN-TEST-004")
        producto.refresh_from_db()
        self.assertEqual(producto.stock, 8)
        self.pedido.refresh_from_db()
        self.assertTrue(self.pedido.stock_descontado)
