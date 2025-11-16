from django.db import models

ESTADO_CHOICES = [
    ('programada', 'Programada'),
    ('atendida', 'Atendida'),
    ('cancelada', 'Cancelada'),
    ('reprogramada', 'Reprogramada'),
    ('no_asistio', 'No Asistió'),
]

class Cita(models.Model):
    paciente = models.ForeignKey('pacientes.Paciente', on_delete=models.CASCADE, null=True, blank=True)
    nombre_completo = models.CharField("Nombre Completo del Paciente", max_length=200, null=True, blank=True)
    fecha_hora = models.DateTimeField("Fecha y Hora de la Cita")
    motivo = models.TextField("Motivo de la Cita", blank=True, null=True)
    doctor = models.ForeignKey('usuarios.Usuario', on_delete=models.SET_NULL, null=True, blank=True, related_name='citas_asignadas')
    estado = models.CharField("Estado de la Cita", max_length=20, choices=ESTADO_CHOICES, default='programada')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        paciente_nombre = self.paciente.nombre_completo if self.paciente else (self.nombre_completo or 'Sin paciente')
        return f"Cita para {paciente_nombre} el {self.fecha_hora.strftime('%Y-%m-%d %H:%M')}"