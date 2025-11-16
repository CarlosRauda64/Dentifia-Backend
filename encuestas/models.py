from django.db import models

class Encuesta(models.Model):
    fecha = models.DateField(auto_now_add=True)
    observaciones = models.CharField(max_length=256, blank=True, default='')
    nivel_satisfaccion = models.IntegerField(default=0)
    preguntas_respuestas = models.JSONField(default=dict, blank=True)
    