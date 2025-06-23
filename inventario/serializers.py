from rest_framework import serializers
from .models import Insumo, Movimiento_stock

# Serializador principal para el CRUD de Insumos.
class InsumoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Insumo
        fields = ('id', 'nombre', 'descripcion', 'stock_actual', 'activo')
        # Hacemos el stock de solo lectura para que no se pueda modificar directamente.
        read_only_fields = ('stock_actual',)

# Serializador auxiliar para anidar la información del insumo dentro de un movimiento.
class InsumoParaMovimientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Insumo
        fields = ('id', 'nombre', 'activo')

# Serializador de Movimiento de Stock que ahora incluye los datos del insumo.
class Movimiento_stockSerializer(serializers.ModelSerializer):
    # Este campo leerá la información del insumo relacionado usando el serializador auxiliar.
    insumo_data = InsumoParaMovimientoSerializer(source='insumo', read_only=True)

    class Meta:
        model = Movimiento_stock
        # 'insumo' es para escribir (se le pasa el ID)
        # 'insumo_data' es para leer (devuelve el objeto anidado)
        fields = (
            'id', 'tipo', 'fecha', 'cantidad', 'insumo', 'insumo_data',
            'usuario', 'nombre_usuario', 'rol_usuario', 'activo'
        )