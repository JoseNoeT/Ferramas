from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.catalogo.models import Producto
from apps.catalogo.services import obtener_precio_efectivo


class Carrito(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="carrito",
        verbose_name="Usuario",
    )
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Carrito"
        verbose_name_plural = "Carritos"

    def __str__(self):
        return f"Carrito de {self.usuario}"


class ItemCarrito(models.Model):
    carrito = models.ForeignKey(
        Carrito, on_delete=models.CASCADE, related_name="items"
    )
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = "Item de Carrito"
        verbose_name_plural = "Items de Carrito"
        unique_together = ("carrito", "producto")

    def __str__(self):
        return f"{self.cantidad}x {self.producto}"

    @property
    def precio_unitario(self):
        return obtener_precio_efectivo(self.producto)

    @property
    def subtotal(self):
        return self.precio_unitario * self.cantidad


class Pedido(models.Model):
    class Estado(models.TextChoices):
        BORRADOR = "borrador", "Borrador"
        GENERADO = "generado", "Generado"
        APROBADO = "aprobado", "Aprobado"
        RECHAZADO = "rechazado", "Rechazado"
        EN_PREPARACION = "en_preparacion", "En preparación"
        LISTO = "listo", "Listo"
        ENTREGADO = "entregado", "Entregado"

    class TipoEntrega(models.TextChoices):
        RETIRO = "retiro", "Retiro en tienda"
        DESPACHO = "despacho", "Despacho a domicilio"

    class PaymentStatus(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        PAGADO = "pagado", "Pagado"
        RECHAZADO = "rechazado", "Rechazado"
        ERROR = "error", "Error"

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="pedidos",
        verbose_name="Usuario",
    )
    estado = models.CharField(
        max_length=20, choices=Estado.choices, default=Estado.BORRADOR
    )
    tipo_entrega = models.CharField(
        max_length=20, choices=TipoEntrega.choices, default=TipoEntrega.RETIRO
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDIENTE,
    )
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    puntos_usados = models.PositiveIntegerField(default=0)
    descuento_puntos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_final = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock_reservado = models.BooleanField(default=False)
    stock_descontado = models.BooleanField(default=False)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ["-creado_en"]

    def __str__(self):
        return f"Pedido #{self.pk} — {self.usuario}"

    def save(self, *args, **kwargs):
        if self.puntos_usados == 0 and self.descuento_puntos == 0:
            self.total_final = self.total
        return super().save(*args, **kwargs)


class ItemPedido(models.Model):
    class TipoLinea(models.TextChoices):
        PRODUCTO = "producto", "Producto"
        ASESORIA = "asesoria", "Asesoria Maestro/PYME"

    pedido = models.ForeignKey(
        Pedido, on_delete=models.CASCADE, related_name="items"
    )
    tipo_linea = models.CharField(
        max_length=20,
        choices=TipoLinea.choices,
        default=TipoLinea.PRODUCTO,
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    solicitud_asesoria = models.ForeignKey(
        "maestros.SolicitudAsesoria",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    descripcion = models.CharField(max_length=255, blank=True, default="")
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Item de Pedido"
        verbose_name_plural = "Items de Pedido"

    def __str__(self):
        if self.tipo_linea == self.TipoLinea.ASESORIA:
            if self.descripcion:
                detalle = self.descripcion
            elif self.solicitud_asesoria_id:
                detalle = self.solicitud_asesoria.servicio.titulo
            else:
                detalle = "Asesoria"
            return f"{self.cantidad}x {detalle} en Pedido #{self.pedido_id}"

        if self.producto_id:
            return f"{self.cantidad}x {self.producto.nombre} en Pedido #{self.pedido_id}"
        return f"{self.cantidad}x Item sin producto en Pedido #{self.pedido_id}"

    def clean(self):
        if self.tipo_linea == self.TipoLinea.PRODUCTO and not self.producto_id:
            raise ValidationError("Las lineas de tipo producto requieren un producto asociado.")
        if self.tipo_linea == self.TipoLinea.ASESORIA and not self.solicitud_asesoria_id:
            raise ValidationError("Las lineas de tipo asesoria requieren una solicitud de asesoria asociada.")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    @property
    def subtotal(self):
        return self.precio_unitario * self.cantidad
