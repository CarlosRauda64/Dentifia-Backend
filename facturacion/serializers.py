from rest_framework import serializers
from .models import Factura, DetalleFactura


class DetalleFacturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleFactura
        exclude = ['factura'] 


class FacturaSerializer(serializers.ModelSerializer):
    detalles = DetalleFacturaSerializer(many=True)
    paciente_nombre = serializers.SerializerMethodField()  # Para mostrar nombre
    monto_total = serializers.DecimalField(max_digits=19, decimal_places=0, required=False)
    
    class Meta:
        model = Factura
        fields = '__all__'
    
    def validate(self, data):
        """Validar que el monto_total coincida con la suma de detalles"""
        detalles = data.get('detalles', [])
        monto_total = data.get('monto_total', 0)
        
        if detalles:
            monto_calculado = 0
            for detalle in detalles:
                precio = float(detalle['precio_unitario'])
                cantidad = int(detalle['cantidad'])
                monto_calculado += precio * cantidad
            
            monto_calculado = int(round(monto_calculado))
            
            # Si se proporciona monto_total, debe coincidir
            if monto_total and monto_total != monto_calculado:
                raise serializers.ValidationError(
                    f"El monto_total ({monto_total}) no coincide con la suma de detalles ({monto_calculado})"
                )
        
        return data
    
    def get_paciente_nombre(self, obj):
        if obj.paciente:
            return obj.paciente.nombre_completo
        return None

    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles', [])
        
        # Calcular monto_total automáticamente
        monto_total = 0
        for detalle in detalles_data:
            precio = float(detalle['precio_unitario'])
            cantidad = int(detalle['cantidad'])
            monto_total += precio * cantidad
        
        # Redondear a entero (sin decimales)
        validated_data['monto_total'] = int(round(monto_total))
        
        factura = Factura.objects.create(**validated_data)
        for detalle_data in detalles_data:
            DetalleFactura.objects.create(factura=factura, **detalle_data)
        return factura

    def update(self, instance, validated_data):
        detalles_data = validated_data.pop('detalles', [])

        # Calcular monto_total automáticamente si hay detalles
        if detalles_data:
            monto_total = 0
            for detalle in detalles_data:
                precio = float(detalle['precio_unitario'])
                cantidad = int(detalle['cantidad'])
                monto_total += precio * cantidad
            
            # Redondear a entero (sin decimales)
            validated_data['monto_total'] = int(round(monto_total))

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




