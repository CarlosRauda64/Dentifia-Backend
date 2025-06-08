from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import UserSerializer
from .models import Usuario
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

@api_view(['POST'])
def login(request):
    usuario = get_object_or_404(Usuario, usuario=request.data['usuario'])
    if not usuario.check_password(request.data['password']):
        return Response({"error":"Contraseña invalida"}, status=status.HTTP_400_BAD_REQUEST)
    token, created = Token.objects.get_or_create(user=usuario)
    serializer = UserSerializer(instance=usuario)

    return Response({"token": token.key, "usuario": serializer.data},
                    status=status.HTTP_200_OK)

@api_view(['POST'])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        user = Usuario.objects.get(usuario=serializer.data['usuario'])
        user.set_password(serializer.data['password'])
        user.save()

        token = Token.objects.create(user=user)
        return Response({'token': token.key, "usuario": serializer.data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def profile(request):
    usuario = request.user
    serializer = UserSerializer(instance=usuario)
    data = serializer.data
    # Solo enviar usuario y email
    filtered_data = {
        "usuario": data.get("usuario"),
        "email": data.get("email"),
        "nombre": data.get("nombre"),
        "apellido": data.get("apellido"),
        "rol": data.get("rol"),
    }
    return Response(filtered_data, 
                    status=status.HTTP_200_OK)