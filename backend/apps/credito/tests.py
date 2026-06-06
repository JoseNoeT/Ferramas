from django.test import TestCase

from apps.credito import services as credito_services
from apps.credito.models import CuentaCredito, CuotaCredito, MovimientoCredito
from apps.maestros.models import PerfilMaestroPyme
from apps.pagos import services as pagos_services
from apps.pagos.models import Pago
from apps.pedidos.models import Pedido
from apps.usuarios.models import Usuario


class CreditoServicesTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            email="maestro.credito@test.com",
            password="Test123456",
            rol=Usuario.Rol.CLIENTE,
        )
        self.perfil = PerfilMaestroPyme.objects.create(
            usuario=self.usuario,
            tipo=PerfilMaestroPyme.Tipo.MAESTRO,
            rut="11.111.111-1",
            rubro="Construccion",
            oficio="Albanil",
            telefono="+56911111111",
            direccion="Calle 123",
            estado=PerfilMaestroPyme.Estado.APROBADO,
        )
        self.cuenta = CuentaCredito.objects.create(
            maestro=self.perfil,
            cupo_aprobado=200000,
            saldo_usado=0,
            estado=CuentaCredito.Estado.ACTIVA,
        )
        self.pedido = Pedido.objects.create(
            usuario=self.usuario,
            estado=Pedido.Estado.GENERADO,
            subtotal=60000,
            total=60000,
            total_final=60000,
        )

    def test_registrar_compra_crea_movimiento_y_cuotas_con_fk_pedido(self):
        movimiento = credito_services.registrar_compra_ferrecredito(
            self.cuenta,
            pedido=self.pedido,
            monto=self.pedido.total_final,
            cantidad_cuotas=3,
        )

        self.assertEqual(movimiento.tipo, MovimientoCredito.Tipo.COMPRA)
        self.assertEqual(movimiento.pedido_id, self.pedido.pk)
        self.assertEqual(
            CuotaCredito.objects.filter(cuenta=self.cuenta, pedido=self.pedido).count(),
            3,
        )

    def test_registrar_compra_no_duplica_movimiento_ni_pago_para_mismo_pedido(self):
        movimiento_1 = credito_services.registrar_compra_ferrecredito(
            self.cuenta,
            pedido=self.pedido,
            monto=self.pedido.total_final,
            cantidad_cuotas=2,
        )
        movimiento_2 = credito_services.registrar_compra_ferrecredito(
            self.cuenta,
            pedido=self.pedido,
            monto=self.pedido.total_final,
            cantidad_cuotas=2,
        )

        pago_1 = pagos_services.registrar_pago_ferrecredito(
            self.pedido,
            movimiento_credito=movimiento_1,
            usuario=self.usuario,
        )
        pago_2 = pagos_services.registrar_pago_ferrecredito(
            self.pedido,
            movimiento_credito=movimiento_2,
            usuario=self.usuario,
        )

        self.assertEqual(movimiento_1.pk, movimiento_2.pk)
        self.assertEqual(
            MovimientoCredito.objects.filter(
                cuenta=self.cuenta,
                pedido=self.pedido,
                tipo=MovimientoCredito.Tipo.COMPRA,
            ).count(),
            1,
        )
        self.assertEqual(pago_1.pk, pago_2.pk)
        self.assertEqual(
            Pago.objects.filter(
                pedido=self.pedido,
                medio_pago=Pago.MedioPago.FERRECREDITO,
            ).count(),
            1,
        )

    def test_ferrecredito_aprobado_deja_pedido_pagado(self):
        movimiento = credito_services.registrar_compra_ferrecredito(
            self.cuenta,
            pedido=self.pedido,
            monto=self.pedido.total_final,
            cantidad_cuotas=1,
        )
        pagos_services.registrar_pago_ferrecredito(
            self.pedido,
            movimiento_credito=movimiento,
            usuario=self.usuario,
        )

        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.payment_status, Pedido.PaymentStatus.PAGADO)
