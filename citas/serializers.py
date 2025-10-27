from rest_framework import serializers
from .models import Cita
from django.utils import timezone # Importante para timezones

class CitaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cita
        fields = '__all__' # O especifica los campos que necesites

    def validate_fecha_hora(self, value):
        """
        Valida que no exista otra cita en el mismo horario.
        """
        # Asegurarnos que la fecha sea "aware" (tenga timezone)
        if timezone.is_naive(value):
            # Si es naive, puedes asignarle la zona horaria por defecto de tu proyecto
            value = timezone.make_aware(value, timezone.get_default_timezone())

        # Revisar si ya existe una cita en la base de datos con esa fecha y hora
        if Cita.objects.filter(fecha_hora=value).exists():
            raise serializers.ValidationError(
                "Ya existe una cita programada para esta fecha y hora. Por favor, elija otro horario."
            )
        
        # Opcional: Validar que la fecha no sea en el pasado
        if value < timezone.now():
            raise serializers.ValidationError("No se pueden crear citas en fechas pasadas.")

        return value

