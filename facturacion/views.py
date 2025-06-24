from rest_framework import viewsets
from .models import Factura, DetalleFactura
from .serializers import FacturaSerializer, DetalleFacturaSerializer
from rest_framework import status, permissions, viewsets
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response


class FacturaViewSet(viewsets.ModelViewSet):
    queryset = Factura.objects.all()
    serializer_class = FacturaSerializer


class DetalleFacturaViewSet(viewsets.ModelViewSet):
    queryset = DetalleFactura.objects.all()
    serializer_class = DetalleFacturaSerializer

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def eliminar_factura(request, pk):
    factura = get_object_or_404(Factura, idfactura=pk)
    factura.activo = False  # Marcar como inactivo en lugar de eliminar
    factura.estado = 'CANCELADA'  
    factura.save()
    return Response(status=status.HTTP_200_OK)