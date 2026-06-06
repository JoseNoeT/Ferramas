from django.test import TestCase

from apps.catalogo.models import Categoria, Producto
from apps.inventario.models import MovimientoInventario
from apps.pedidos import services as pedidos_services
from apps.pedidos.models import Carrito, ItemCarrito
from apps.usuarios.models import Usuario


class InventarioPedidoFlowTests(TestCase):
	def setUp(self):
		self.usuario = Usuario.objects.create_user(
			email="cliente.inventario@test.com",
			password="Test123456",
			rol=Usuario.Rol.CLIENTE,
		)
		self.categoria = Categoria.objects.create(nombre="Herramientas", slug="herramientas")
		self.producto = Producto.objects.create(
			nombre="Martillo QA",
			slug="martillo-qa",
			descripcion="Producto de prueba",
			precio=10000,
			stock=10,
			activo=True,
			categoria=self.categoria,
		)

	def _crear_pedido_desde_carrito(self, cantidad=2):
		carrito = Carrito.objects.create(usuario=self.usuario)
		ItemCarrito.objects.create(carrito=carrito, producto=self.producto, cantidad=cantidad)
		return pedidos_services.crear_pedido_desde_carrito(self.usuario, "retiro")

	def test_no_crear_pedido_si_stock_insuficiente(self):
		carrito = Carrito.objects.create(usuario=self.usuario)
		ItemCarrito.objects.create(carrito=carrito, producto=self.producto, cantidad=99)

		with self.assertRaises(ValueError):
			pedidos_services.crear_pedido_desde_carrito(self.usuario, "retiro")

	def test_crear_pedido_reserva_stock_y_crea_movimiento(self):
		pedido = self._crear_pedido_desde_carrito(cantidad=3)
		self.producto.refresh_from_db()
		pedido.refresh_from_db()

		self.assertEqual(self.producto.stock, 7)
		self.assertTrue(pedido.stock_reservado)
		self.assertFalse(pedido.stock_descontado)
		self.assertTrue(
			MovimientoInventario.objects.filter(
				pedido=pedido,
				producto=self.producto,
				tipo_movimiento=MovimientoInventario.TipoMovimiento.RESERVA,
			).exists()
		)
		mov = MovimientoInventario.objects.get(
			pedido=pedido,
			producto=self.producto,
			tipo_movimiento=MovimientoInventario.TipoMovimiento.RESERVA,
		)
		self.assertEqual(mov.stock_anterior, 10)
		self.assertEqual(mov.stock_nuevo, 7)
		self.assertEqual(mov.usuario, self.usuario)

	def test_rechazar_pedido_libera_stock(self):
		pedido = self._crear_pedido_desde_carrito(cantidad=4)
		pedidos_services.rechazar_pedido(pedido, usuario=self.usuario)

		self.producto.refresh_from_db()
		pedido.refresh_from_db()

		self.assertEqual(self.producto.stock, 10)
		self.assertFalse(pedido.stock_reservado)
		self.assertTrue(
			MovimientoInventario.objects.filter(
				pedido=pedido,
				producto=self.producto,
				tipo_movimiento=MovimientoInventario.TipoMovimiento.LIBERACION,
			).exists()
		)

	def test_doble_rechazo_no_libera_dos_veces(self):
		pedido = self._crear_pedido_desde_carrito(cantidad=2)
		pedidos_services.rechazar_pedido(pedido, usuario=self.usuario)

		with self.assertRaises(ValueError):
			pedidos_services.rechazar_pedido(pedido, usuario=self.usuario)

		self.producto.refresh_from_db()
		self.assertEqual(self.producto.stock, 10)
		self.assertEqual(
			MovimientoInventario.objects.filter(
				pedido=pedido,
				producto=self.producto,
				tipo_movimiento=MovimientoInventario.TipoMovimiento.LIBERACION,
			).count(),
			1,
		)

	def test_preparar_pedido_no_descuenta_doble(self):
		pedido = self._crear_pedido_desde_carrito(cantidad=2)
		pedidos_services.aprobar_pedido(pedido, usuario=self.usuario)
		pedidos_services.poner_en_preparacion(pedido, usuario=self.usuario)

		self.producto.refresh_from_db()
		self.assertEqual(self.producto.stock, 8)
		self.assertTrue(
			MovimientoInventario.objects.filter(
				pedido=pedido,
				producto=self.producto,
				tipo_movimiento=MovimientoInventario.TipoMovimiento.AJUSTE,
				cantidad=0,
				motivo="Inicio de preparacion en bodega.",
				usuario=self.usuario,
			).exists()
		)

	def test_marcar_listo_conserva_stock_y_trazabilidad(self):
		pedido = self._crear_pedido_desde_carrito(cantidad=2)
		pedidos_services.aprobar_pedido(pedido, usuario=self.usuario)
		pedidos_services.poner_en_preparacion(pedido, usuario=self.usuario)
		pedidos_services.marcar_pedido_listo(pedido, usuario=self.usuario)

		self.producto.refresh_from_db()
		self.assertEqual(self.producto.stock, 8)
		self.assertTrue(
			MovimientoInventario.objects.filter(
				pedido=pedido,
				producto=self.producto,
				tipo_movimiento=MovimientoInventario.TipoMovimiento.AJUSTE,
				cantidad=0,
				motivo="Pedido marcado como listo en bodega.",
				usuario=self.usuario,
			).exists()
		)
