from rest_framework import serializers
from .models import Factura, DetalleFactura


class DetalleFacturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleFactura
        exclude = ['factura'] 


class FacturaSerializer(serializers.ModelSerializer):
    detalles = DetalleFacturaSerializer(many=True)
    paciente_nombre = serializers.SerializerMethodField()  # Para mostrar nombre
    
    class Meta:
        model = Factura
        fields = '__all__'
    
    def get_paciente_nombre(self, obj):
        if obj.paciente:
            return obj.paciente.nombre_completo
        return None

    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles', [])
        factura = Factura.objects.create(**validated_data)
        for detalle_data in detalles_data:
            DetalleFactura.objects.create(factura=factura, **detalle_data)
        return factura

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




