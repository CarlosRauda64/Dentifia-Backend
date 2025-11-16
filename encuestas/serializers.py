from rest_framework import serializers
from .models import Encuesta

class EncuestaSerializer(serializers.ModelSerializer):
    observaciones = serializers.CharField(required=False, allow_blank=True, default='')
    nivel_satisfaccion = serializers.IntegerField(read_only=True)  # Se calcula automáticamente
    
    class Meta:
        model = Encuesta
        fields = ('id', 'fecha', 'observaciones', 'nivel_satisfaccion', 'preguntas_respuestas')
    
    def mapear_respuesta_a_valor(self, respuesta):
        """
        Mapea las respuestas de texto a valores numéricos para el cálculo del promedio.
        """
        if not respuesta:
            return 3
        
        # Normalizar la respuesta
        respuesta_str = str(respuesta).strip()
        respuesta_lower = respuesta_str.lower()
        
        # Mapeo exacto (case-insensitive)
        mapeo_exacto = {
            # Escala 5 puntos (Excelente a Mala)
            'excelente': 5,
            'muy buena': 4,
            'muy bueno': 4,
            'buena': 3,
            'bueno': 3,
            'regular': 2,
            'mala': 1,
            'malo': 1,
            # Escala Sí/No/No estoy seguro
            'sí': 5,
            'si': 5,
            'no': 1,
            'no estoy seguro': 3,
        }
        
        # Buscar coincidencia exacta
        if respuesta_lower in mapeo_exacto:
            return mapeo_exacto[respuesta_lower]
        
        # Buscar coincidencia parcial (palabras clave)
        if 'excelente' in respuesta_lower or 'perfecto' in respuesta_lower or 'genial' in respuesta_lower:
            return 5
        elif 'muy buena' in respuesta_lower or 'muy bueno' in respuesta_lower or 'muy bien' in respuesta_lower:
            return 4
        elif 'buena' in respuesta_lower or 'bueno' in respuesta_lower or 'bien' in respuesta_lower or 'aceptable' in respuesta_lower:
            return 3
        elif 'regular' in respuesta_lower or 'normal' in respuesta_lower or 'promedio' in respuesta_lower:
            return 2
        elif 'mala' in respuesta_lower or 'malo' in respuesta_lower or ('mal' in respuesta_lower and 'muy' not in respuesta_lower) or 'deficiente' in respuesta_lower:
            return 1
        
        # Valor por defecto si no se puede mapear
        return 3
    
    def calcular_nivel_satisfaccion(self, preguntas_respuestas):
        """
        Calcula el nivel de satisfacción como promedio ponderado de las respuestas.
        """
        if not preguntas_respuestas or not isinstance(preguntas_respuestas, dict):
            return 3  # Valor por defecto si no hay respuestas
        
        valores = []
        for pregunta, respuesta in preguntas_respuestas.items():
            if respuesta:
                valor = self.mapear_respuesta_a_valor(str(respuesta))
                valores.append(valor)
        
        if not valores:
            return 3  # Valor por defecto si no hay valores válidos
        
        # Calcular promedio y redondear al entero más cercano
        promedio = sum(valores) / len(valores)
        nivel = round(promedio)
        
        # Asegurar que esté en el rango 1-5
        nivel = max(1, min(5, nivel))
        
        return nivel
    
    def to_representation(self, instance):
        """
        Recalcula el nivel_satisfaccion al leer una encuesta si tiene preguntas_respuestas.
        Esto asegura que encuestas antiguas también tengan el valor correcto.
        """
        representation = super().to_representation(instance)
        
        # Si hay preguntas_respuestas, recalcular el nivel_satisfaccion
        if instance.preguntas_respuestas and isinstance(instance.preguntas_respuestas, dict) and len(instance.preguntas_respuestas) > 0:
            nivel_calculado = self.calcular_nivel_satisfaccion(instance.preguntas_respuestas)
            representation['nivel_satisfaccion'] = nivel_calculado
            
            # Si el valor en la BD es diferente, actualizarlo
            if instance.nivel_satisfaccion != nivel_calculado:
                instance.nivel_satisfaccion = nivel_calculado
                instance.save(update_fields=['nivel_satisfaccion'])
        
        return representation
    
    def create(self, validated_data):
        """
        Crea una encuesta y calcula automáticamente el nivel_satisfaccion
        basado en las respuestas de preguntas_respuestas.
        """
        preguntas_respuestas = validated_data.get('preguntas_respuestas', {})
        nivel_satisfaccion = self.calcular_nivel_satisfaccion(preguntas_respuestas)
        validated_data['nivel_satisfaccion'] = nivel_satisfaccion
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """
        Actualiza una encuesta y recalcula el nivel_satisfaccion si se modifican
        las preguntas_respuestas.
        """
        preguntas_respuestas = validated_data.get('preguntas_respuestas', instance.preguntas_respuestas)
        nivel_satisfaccion = self.calcular_nivel_satisfaccion(preguntas_respuestas)
        validated_data['nivel_satisfaccion'] = nivel_satisfaccion
        return super().update(instance, validated_data)