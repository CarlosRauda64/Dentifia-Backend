from rest_framework import serializers
from .models import Insumo,Movimiento_stock

class InsumoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Insumo
        fields = ('nombre','descripcion','stock_actual')

class Movimiento_stockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movimiento_stock
        fields= ('tipo','fecha','cantidad')
