from rest_framework import serializers
from .models import Usuario
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = [
            'id', 
            'usuario', 
            'password',
            'email', 
            'nombre',
            'apellido',
            'rol',
            ]

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'usuario'