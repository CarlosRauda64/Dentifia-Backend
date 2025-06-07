from rest_framework import serializers
from .models import Usuario

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

