from django.shortcuts import get_object_or_404, render
from rest_framework import viewsets,permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import timedelta, datetime
from django.utils.dateparse import parse_date
from rest_framework.decorators import authentication_classes, permission_classes
from .models import Cita
from .serializers import CitaSerializer

class CitaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para manejar el CRUD de Citas.
    - La lista (GET) muestra todas las citas.
    - Requiere autenticación JWT.
    """
    queryset = Cita.objects.all()
    serializer_class = CitaSerializer
    permission_classes = [IsAuthenticated]

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_citas(request):
    """
    Lista todas las citas con filtros opcionales:
    - paciente_id: Filtrar por ID de paciente
    - desde: Fecha inicial (formato YYYY-MM-DD)
    - hasta: Fecha final (formato YYYY-MM-DD)
    """
    citas = Cita.objects.all()
    
    # Filtro por paciente
    paciente_id = request.query_params.get('paciente_id', None)
    if paciente_id:
        try:
            citas = citas.filter(paciente_id=int(paciente_id))
        except (ValueError, TypeError):
            pass
    
    # Filtro por rango de fechas
    desde = request.query_params.get('desde', None)
    hasta = request.query_params.get('hasta', None)
    
    if desde:
        try:
            desde_date = parse_date(desde)
            if desde_date:
                citas = citas.filter(fecha_hora__date__gte=desde_date)
        except (ValueError, TypeError):
            pass
    
    if hasta:
        try:
            hasta_date = parse_date(hasta)
            if hasta_date:
                citas = citas.filter(fecha_hora__date__lte=hasta_date)
        except (ValueError, TypeError):
            pass
    
    serializer = CitaSerializer(citas, many=True)
    return Response(serializer.data)

# views.py (tu función insertar_cita actualizada)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def insertar_cita(request):
    serializer = CitaSerializer(data=request.data)
    
    # La validación personalizada se ejecuta aquí automáticamente
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    # Si la validación falla (por cualquier motivo), devuelve los errores
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def eliminar_cita(request, cita_id):
    try:
        cita = get_object_or_404(Cita, id=cita_id)
        cita.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)