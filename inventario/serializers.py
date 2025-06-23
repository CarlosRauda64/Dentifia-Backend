from rest_framework import serializers
from .models import Insumo,Movimiento_stock

class InsumoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Insumo
        fields = ('id','nombre','descripcion','stock_actual', 'activo')

class Movimiento_stockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movimiento_stock
        fields= ('id','tipo','fecha','cantidad','insumo','usuario','nombre_usuario','rol_usuario','activo')
