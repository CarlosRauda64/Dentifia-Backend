from django.shortcuts import get_object_or_404, render
from rest_framework import viewsets,permissions
from .models import Insumo, Movimiento_stock
from .serializers import InsumoSerializer, Movimiento_stockSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import authentication_classes, permission_classes

# Create your views here.
class InsumoViewSet(viewsets.ModelViewSet):
   
    queryset = Insumo.objects.all()
    serializer_class = InsumoSerializer

class MovimientoStockViewSet(viewsets.ModelViewSet):
    """ permission_classes = permissions.IsAuthenticated """
    queryset = Movimiento_stock.objects.all()
    serializer_class = Movimiento_stockSerializer

""" Metodo de insercion de movimiento_stock """

@api_view(['POST'])
def insertar_movimiento(request):
    try:
        serializer = Movimiento_stockSerializer(data=request.data)
        
        if serializer.is_valid():
            tipo=serializer.validated_data.get("tipo")
            if tipo == 'entrada':
                insumo = get_object_or_404(Insumo, id=serializer.validated_data['insumo'].id)
                print(insumo.id)
                insumo.stock_actual+= serializer.validated_data['cantidad']
                insumo.save()
            elif tipo == 'salida':
                insumo = get_object_or_404(Insumo, id=serializer.validated_data['insumo'].id)
                if insumo.stock_actual >= serializer.validated_data['cantidad']:
                    insumo.stock_actual -= serializer.validated_data['cantidad']
                    insumo.save()
                else:
                    return Response({"error": "Stock insuficiente para la salida"}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['PUT'])
def actualizar_movimiento(request, id):
    try:
        movimiento = get_object_or_404(Movimiento_stock, id=id)
        cantidad_anterior = movimiento.cantidad
        tipo_anterior = movimiento.tipo
        

        serializer = Movimiento_stockSerializer(movimiento, data=request.data, partial=True)
        if serializer.is_valid():
            nuevo_tipo = serializer.validated_data.get("tipo", tipo_anterior)
            nueva_cantidad = serializer.validated_data.get("cantidad", cantidad_anterior)
            insumo = serializer.validated_data.get("insumo")

            if tipo_anterior == 'entrada':
                insumo.stock_actual -= cantidad_anterior
            elif tipo_anterior == 'salida':
                insumo.stock_actual += cantidad_anterior
            insumo.save()

            if nuevo_tipo == 'entrada':
                insumo.stock_actual += nueva_cantidad
            elif nuevo_tipo == 'salida':
                if insumo.stock_actual >= nueva_cantidad:
                    insumo.stock_actual -= nueva_cantidad
                else:
                    return Response({"error": "Stock insuficiente para la salida"}, status=status.HTTP_400_BAD_REQUEST)

            insumo.save()
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    
""" Este es el metodo eliminar de Movimiento_stock """
@api_view(['DELETE'])
def eliminar_movimiento(request,id):
    try:
        movimiento = get_object_or_404(Movimiento_stock, id=id)
        if movimiento.tipo == 'entrada':
            insumo = get_object_or_404(Insumo, id=movimiento.insumo.id)
            insumo.stock_actual -= movimiento.cantidad
            if insumo.stock_actual < 0:
                insumo.stock_actual = 0
            insumo.save()
        elif movimiento.tipo == 'salida':
            insumo = get_object_or_404(Insumo, id=movimiento.insumo.id)
            insumo.stock_actual += movimiento.cantidad
            insumo.save()
        movimiento.activo = False
        movimiento.save()
        return Response({"response": "Movimiento desactivado correctamente"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    
    