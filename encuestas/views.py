from django.shortcuts import get_object_or_404, render
from rest_framework import viewsets,permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import authentication_classes, permission_classes
from .models import Encuesta
from .serializers import EncuestaSerializer


class EncuestaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para manejar el CRUD de Encuestas.
    - La lista (GET) muestra todas las encuestas.
    """
    queryset = Encuesta.objects.all()
    serializer_class = EncuestaSerializer

@api_view(['GET'])
def listar_encuestas(request):
    encuestas = Encuesta.objects.all()
    serializer = EncuestaSerializer(encuestas, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def insertar_encuesta(request):
    try:
        serializer = EncuestaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['DELETE'])
def eliminar_encuesta(request, encuesta_id):
    try:
        encuesta = get_object_or_404(Encuesta, id=encuesta_id)
        encuesta.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)