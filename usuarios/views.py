from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import (
    UserSerializer,
    CustomTokenObtainPairSerializer
)
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import Usuario
from rest_framework import status, permissions, viewsets
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

@api_view(['POST'])
def login(request):
    usuario = get_object_or_404(Usuario, usuario=request.data['usuario'])
    if not usuario.check_password(request.data['password']):
        return Response({"error":"Contraseña invalida"}, status=status.HTTP_400_BAD_REQUEST)
    serializer = UserSerializer(instance=usuario)

    return Response({"usuario": serializer.data},
                    status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def profile(request):
    usuario = request.user
    serializer = UserSerializer(instance=usuario)
    data = serializer.data
    # Solo enviar usuario y email
    filtered_data = {
        "id": data.get("id"),
        "usuario": data.get("usuario"),
        "email": data.get("email"),
        "nombre": data.get("nombre"),
        "apellido": data.get("apellido"),
        "rol": data.get("rol"),
    }
    return Response(filtered_data, 
                    status=status.HTTP_200_OK)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer 

""" Crear un nuevo usuario. """
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        user = Usuario.objects.get(usuario=serializer.data['usuario'])
        user.set_password(serializer.data['password'])
        user.save()
        return Response({"usuario": serializer.data.get("usuario")}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def editar_usuario(request, id):
    usuario = get_object_or_404(Usuario, id=id)
    request_data = request.data.copy()
    if 'password' in request_data and request_data['password'].strip() == '':
        request_data.pop('password')
    serializer = UserSerializer(usuario, data=request_data, partial=True)
    if serializer.is_valid():
        serializer.save()
        user = Usuario.objects.get(usuario=serializer.data['usuario'])
        user.set_password(serializer.data['password'])
        user.save()
        return Response({"response": "Usuario editado correctamente"}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

""" Listar usuarios registrados. """
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_usuarios(request):
    usuarios = Usuario.objects.all()
    serializer = UserSerializer(instance=usuarios, many=True)
    data = serializer.data
    filtered_data = []
    for user in data:
        filtered_data.append({
            "id": user.get("id"),
            "usuario": user.get("usuario"),
            "email": user.get("email"),
            "nombre": user.get("nombre"),
            "apellido": user.get("apellido"),
            "rol": user.get("rol"),
        })
    return Response(filtered_data, status=status.HTTP_200_OK)

""" ViewSet para manejar las operaciones CRUD de Usuario, menos el insertar. """
class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'put', 'patch', 'delete']
