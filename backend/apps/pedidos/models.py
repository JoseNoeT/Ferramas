from django.conf import settings
from django.db import models

from apps.catalogo.models import Producto


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
    def subtotal(self):
        return self.producto.precio * self.cantidad


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
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ["-creado_en"]

    def __str__(self):
        return f"Pedido #{self.pk} — {self.usuario}"


class ItemPedido(models.Model):
    pedido = models.ForeignKey(
        Pedido, on_delete=models.CASCADE, related_name="items"
    )
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Item de Pedido"
        verbose_name_plural = "Items de Pedido"

    def __str__(self):
        return f"{self.cantidad}x {self.producto} en Pedido #{self.pedido_id}"

    @property
    def subtotal(self):
        return self.precio_unitario * self.cantidad
