from rest_framework import serializers

from apps.pedidos.models import ItemCarrito, ItemPedido, Pedido


class ProductoResumenSerializer(serializers.Serializer):
	id = serializers.IntegerField()
	nombre = serializers.CharField()
	slug = serializers.CharField()
	imagen = serializers.CharField(allow_blank=True)


class ItemCarritoSerializer(serializers.ModelSerializer):
	producto = serializers.SerializerMethodField()
	precio_unitario = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
	subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

	class Meta:
		model = ItemCarrito
		fields = ["id", "producto", "cantidad", "precio_unitario", "subtotal"]

	def get_producto(self, obj):
		return ProductoResumenSerializer(obj.producto).data


class ResumenCarritoSerializer(serializers.Serializer):
	items = ItemCarritoSerializer(many=True)
	subtotal = serializers.DecimalField(max_digits=12, decimal_places=2)
	total = serializers.DecimalField(max_digits=12, decimal_places=2)


class AgregarCarritoSerializer(serializers.Serializer):
	producto_id = serializers.IntegerField(min_value=1)
	cantidad = serializers.IntegerField(min_value=1, default=1)


class EliminarCarritoSerializer(serializers.Serializer):
	item_id = serializers.IntegerField(min_value=1)


class CrearPedidoSerializer(serializers.Serializer):
	tipo_entrega = serializers.ChoiceField(
		choices=[Pedido.TipoEntrega.RETIRO, Pedido.TipoEntrega.DESPACHO],
		default=Pedido.TipoEntrega.RETIRO,
	)


class ItemPedidoSerializer(serializers.ModelSerializer):
	producto = serializers.SerializerMethodField()
	subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

	class Meta:
		model = ItemPedido
		fields = ["id", "producto", "cantidad", "precio_unitario", "subtotal"]

	def get_producto(self, obj):
		return ProductoResumenSerializer(obj.producto).data


class PedidoSerializer(serializers.ModelSerializer):
	items = ItemPedidoSerializer(many=True)

	class Meta:
		model = Pedido
		fields = [
			"id",
			"estado",
			"tipo_entrega",
			"subtotal",
			"total",
			"creado_en",
			"items",
		]
