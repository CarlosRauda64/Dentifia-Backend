from rest_framework import serializers
from .models import Factura, DetalleFactura


class DetalleFacturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleFactura
        exclude = ['factura'] 


class FacturaSerializer(serializers.ModelSerializer):
    detalles = DetalleFacturaSerializer(many=True)
    montoAbonado = serializers.FloatField(source='get_monto_abonado', read_only=True)


    class Meta:
        model = Factura
        fields = '__all__'

    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles', [])
        factura = Factura.objects.create(**validated_data)
        for detalle_data in detalles_data:
            DetalleFactura.objects.create(factura=factura, **detalle_data)
        return factura


    def create(self, validated_data):
        montoAbonado = validated_data.pop("montoAbonado", 0)
        print ("Monto abonado:", montoAbonado)
        return super().create(validated_data)

    def update(self, instance, validated_data):  # 👈 Este método debe estar al mismo nivel que create
        detalles_data = validated_data.pop('detalles', [])

        # Actualiza los campos de la factura
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Borra los detalles antiguos
        instance.detalles.all().delete()

        # Crea los nuevos detalles
        for detalle_data in detalles_data:
            DetalleFactura.objects.create(factura=instance, **detalle_data)

        return instance




