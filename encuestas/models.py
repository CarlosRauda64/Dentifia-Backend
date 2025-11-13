from django.db import models

class Encuesta(models.Model):
    
    observaciones = models.CharField(max_length=256)
    nivel_satisfaccion = models.IntegerField(default=0)

    