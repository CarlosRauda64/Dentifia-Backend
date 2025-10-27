from django.shortcuts import get_object_or_404, render
from rest_framework import viewsets,permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import timedelta
from rest_framework.decorators import authentication_classes, permission_classes
from .models import Cita
from .serializers import CitaSerializer

class CitaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para manejar el CRUD de Citas.
    - La lista (GET) muestra todas las citas.
    """
    queryset = Cita.objects.all()
    serializer_class = CitaSerializer

@api_view(['GET'])
def listar_citas(request):
    citas = Cita.objects.all()
    serializer = CitaSerializer(citas, many=True)
    return Response(serializer.data)

# views.py (tu función insertar_cita actualizada)

@api_view(['POST'])
def insertar_cita(request):
    serializer = CitaSerializer(data=request.data)
    
    # La validación personalizada se ejecuta aquí automáticamente
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    # Si la validación falla (por cualquier motivo), devuelve los errores
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def eliminar_cita(request, cita_id):
    try:
        cita = get_object_or_404(Cita, id=cita_id)
        cita.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)