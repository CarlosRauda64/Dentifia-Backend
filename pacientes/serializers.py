from rest_framework import serializers
from .models import Paciente

# Serializer para datos médicos (validación flexible - todos opcionales)
class DatosMedicosSerializer(serializers.Serializer):
    alergias = serializers.CharField(allow_blank=True, required=False)
    medicamentos = serializers.CharField(allow_blank=True, required=False)
    ultimaVisita = serializers.CharField(allow_blank=True, required=False)
    nombreDentistaAnterior = serializers.CharField(allow_blank=True, required=False)
    numeroDentistaAnterior = serializers.CharField(allow_blank=True, required=False)
    recomendadorDeClinica = serializers.CharField(allow_blank=True, required=False)
    atendidoPorMedico = serializers.BooleanField(required=False)
    razonesDeTratamiento = serializers.CharField(allow_blank=True, required=False)
    nombreMedico = serializers.CharField(allow_blank=True, required=False)
    telefonoMedico = serializers.CharField(allow_blank=True, required=False)
    tomaMedicamento = serializers.BooleanField(required=False)
    razonTomaMedicamento = serializers.CharField(allow_blank=True, required=False)
    enfermedades = serializers.CharField(allow_blank=True, required=False)
    hemorragiaDespuesDeIntervencion = serializers.BooleanField(required=False)
    alergicoAnalgesicoDental = serializers.BooleanField(required=False)
    embarazada = serializers.BooleanField(required=False)
    tiempoEmbarazada = serializers.CharField(allow_blank=True, required=False)
    hijos = serializers.BooleanField(required=False)
    partoNatural = serializers.BooleanField(required=False)
    menstruando = serializers.BooleanField(required=False)

# Serializer principal del paciente
class PacienteSerializer(serializers.ModelSerializer):
    datos_medicos = DatosMedicosSerializer()
    nombre_completo = serializers.ReadOnlyField()
    edad = serializers.ReadOnlyField()
    
    class Meta:
        model = Paciente
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_dui(self, value):
        """Validar formato de DUI si se proporciona"""
        if value:
            # Formato: 12345678-9 (8 dígitos, guión, 1 dígito)
            import re
            if not re.match(r'^\d{8}-\d{1}$', value):
                raise serializers.ValidationError("El DUI debe tener el formato 12345678-9")
        return value
    
    def validate_fecha_nacimiento(self, value):
        """Validar que la fecha de nacimiento sea coherente"""
        from datetime import date
        today = date.today()
        if value > today:
            raise serializers.ValidationError("La fecha de nacimiento no puede ser futura")
        if value.year < 1900:
            raise serializers.ValidationError("La fecha de nacimiento debe ser posterior a 1900")
        return value
    
    def create(self, validated_data):
        """Crear paciente con datos médicos"""
        datos_medicos = validated_data.pop('datos_medicos', {})
        paciente = Paciente.objects.create(**validated_data)
        
        # Actualizar datos médicos si se proporcionaron y no están vacíos
        if datos_medicos and any(value for value in datos_medicos.values() if value):
            paciente.datos_medicos.update(datos_medicos)
            paciente.save()
        
        return paciente
    
    def update(self, instance, validated_data):
        """Actualizar paciente con datos médicos"""
        datos_medicos = validated_data.pop('datos_medicos', None)
        if datos_medicos is not None:
            # Actualizar solo los campos proporcionados
            instance.datos_medicos.update(datos_medicos)
        return super().update(instance, validated_data)

# Serializer para creación (campos obligatorios: nombres, apellidos, fecha_nacimiento, telefono)
class PacienteCreateSerializer(PacienteSerializer):
    class Meta(PacienteSerializer.Meta):
        extra_kwargs = {
            'nombres': {'required': True},
            'apellidos': {'required': True},
            'fecha_nacimiento': {'required': True},
            'telefono': {'required': True},
            # direccion es opcional
        }

# Serializer para listados (campos básicos)
class PacienteListSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.ReadOnlyField()
    edad = serializers.ReadOnlyField()
    
    class Meta:
        model = Paciente
        fields = ['id', 'nombres', 'apellidos', 'nombre_completo', 'dui', 'telefono', 'celular', 'email', 'edad', 'activo', 'created_at']

