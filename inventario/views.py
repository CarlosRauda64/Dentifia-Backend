from django.shortcuts import render
from rest_framework import viewsets,permissions
from .models import Insumo, Movimiento_stock
from .serializers import InsumoSerializer, Movimiento_stockSerializer
from rest_framework.permissions import IsAuthenticated

# Create your views here.
class InsumoViewSet(viewsets.ModelViewSet):
   
    queryset = Insumo.objects.all()
    serializer_class = InsumoSerializer

class MovimientoStockViewSet(viewsets.ModelViewSet):
    permission_classes = permissions.IsAuthenticated
    queryset = Movimiento_stock.objects.all()
    serializer_class = Movimiento_stockSerializer
