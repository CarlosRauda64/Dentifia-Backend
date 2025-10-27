from django.contrib import admin
from .models import Paciente

@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ['nombre_completo', 'telefono', 'edad', 'activo', 'created_at']
    list_filter = ['activo', 'sexo', 'created_at']
    search_fields = ['nombres', 'apellidos', 'telefono', 'dui']
    readonly_fields = ['created_at', 'updated_at', 'edad']
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombres', 'apellidos', 'dui', 'fecha_nacimiento', 'sexo')
        }),
        ('Contacto', {
            'fields': ('telefono', 'celular', 'email', 'direccion')
        }),
        ('Datos Médicos', {
            'fields': ('datos_medicos',),
            'description': 'Datos médicos almacenados como JSON (alergias, medicamentos, historial, etc.)'
        }),
        ('Control', {
            'fields': ('activo', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ['edad']
        return self.readonly_fields