from rest_framework import serializers
from .models import Cita
from django.utils import timezone # Importante para timezones

class CitaSerializer(serializers.ModelSerializer):
    doctor_nombre = serializers.SerializerMethodField()
    paciente_nombres = serializers.SerializerMethodField()
    paciente_apellidos = serializers.SerializerMethodField()
    
    class Meta:
        model = Cita
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'doctor_nombre', 'paciente_nombres', 'paciente_apellidos')

    def get_doctor_nombre(self, obj):
        """Retorna el nombre completo del doctor si existe"""
        if obj.doctor:
            return f"{obj.doctor.nombre} {obj.doctor.apellido}"
        return None

    def get_paciente_nombres(self, obj):
        """Retorna los nombres del paciente si existe"""
        if obj.paciente:
            return obj.paciente.nombres
        return None

    def get_paciente_apellidos(self, obj):
        """Retorna los apellidos del paciente si existe"""
        if obj.paciente:
            return obj.paciente.apellidos
        return None

    def validate_fecha_hora(self, value):
        """
        Valida que no exista otra cita en el mismo horario.
        """
        # Asegurarnos que la fecha sea "aware" (tenga timezone)
        if timezone.is_naive(value):
            # Si es naive, puedes asignarle la zona horaria por defecto de tu proyecto
            value = timezone.make_aware(value, timezone.get_default_timezone())

        # Revisar si ya existe una cita en la base de datos con esa fecha y hora
        # Excluir la cita actual si estamos editando
        instance = self.instance
        queryset = Cita.objects.filter(fecha_hora=value)
        if instance:
            queryset = queryset.exclude(pk=instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError(
                "Ya existe una cita programada para esta fecha y hora. Por favor, elija otro horario."
            )
        
        # Opcional: Validar que la fecha no sea en el pasado
        if value < timezone.now():
            raise serializers.ValidationError("No se pueden crear citas en fechas pasadas.")

        return value

