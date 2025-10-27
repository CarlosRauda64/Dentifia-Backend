from django.db import models

class Cita(models.Model):
    paciente = models.ForeignKey('pacientes.Paciente', on_delete=models.CASCADE,null=True)
    nombre_completo = models.CharField("Nombre Completo del Paciente", max_length=200, null=True)
    fecha_hora = models.DateTimeField("Fecha y Hora de la Cita")
    motivo = models.TextField("Motivo de la Cita", blank=True, null=True)
    
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Cita para {self.paciente.nombre_completo} el {self.fecha_hora.strftime('%Y-%m-%d %H:%M')}"