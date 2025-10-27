from django.db import models
import json

def default_datos_medicos():
    return {
        "alergias": "",
        "medicamentos": "",
        "ultimaVisita": None,
        "nombreDentistaAnterior": "",
        "numeroDentistaAnterior": "",
        "recomendadorDeClinica": "",
        "atendidoPorMedico": False,
        "razonesDeTratamiento": "",
        "nombreMedico": "",
        "telefonoMedico": "",
        "tomaMedicamento": False,
        "razonTomaMedicamento": "",
        "enfermedades": "",
        "hemorragiaDespuesDeIntervencion": False,
        "alergicoAnalgesicoDental": False,
        "embarazada": False,
        "tiempoEmbarazada": "",
        "hijos": False,
        "partoNatural": False,
        "menstruando": False,
    }

class Paciente(models.Model):
    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('X', 'Otro'),
    ]
    
    # Atributos principales (alineados con DB sugerida)
    nombres = models.CharField("Nombres", max_length=200)
    apellidos = models.CharField("Apellidos", max_length=200)
    dui = models.CharField("DUI", max_length=20, unique=True, blank=True, null=True)
    fecha_nacimiento = models.DateField("Fecha de Nacimiento")
    sexo = models.CharField("Sexo", max_length=1, choices=SEXO_CHOICES, blank=True)
    telefono = models.CharField("Teléfono", max_length=20)
    celular = models.CharField("Celular", max_length=20, blank=True, null=True)
    email = models.EmailField("Correo Electrónico", blank=True, null=True)
    direccion = models.TextField("Dirección", blank=True, null=True)
    
    # Datos médicos como JSON (incluye alergias y medicamentos)
    datos_medicos = models.JSONField(default=default_datos_medicos, blank=True)
    
    # Campos de control
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.nombres} {self.apellidos} - {self.telefono}"
    
    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"
    
    @property
    def edad(self):
        from datetime import date
        today = date.today()
        return today.year - self.fecha_nacimiento.year - ((today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))
    
    class Meta:
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['nombres', 'apellidos']),
            models.Index(fields=['telefono']),
            models.Index(fields=['dui']),
        ]