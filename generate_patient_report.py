"""
Script para generar un reporte de pacientes desde el backend
"""
import os
import django
import json
from datetime import datetime, date
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dentifia.settings')
django.setup()

from pacientes.models import Paciente
from django.db.models import Q

def calcular_edad(fecha_nacimiento):
    """Calcula la edad a partir de la fecha de nacimiento"""
    today = date.today()
    return today.year - fecha_nacimiento.year - ((today.month, today.day) < (fecha_nacimiento.month, fecha_nacimiento.day))

def generar_reporte_pacientes(filtros=None):
    """
    Genera un reporte de pacientes con los filtros especificados
    
    Args:
        filtros: dict con opciones:
            - desde: fecha desde (YYYY-MM-DD)
            - hasta: fecha hasta (YYYY-MM-DD)
            - sexo: 'M', 'F', o None
            - rangoEdad: '0-18', '19-35', '36-50', '51-65', '65+', o None
            - busquedaNombre: string para buscar en nombres/apellidos
    """
    filtros = filtros or {}
    
    # Obtener todos los pacientes activos
    pacientes = Paciente.objects.filter(activo=True)
    
    # Filtro por fecha de registro
    desde = filtros.get('desde')
    hasta = filtros.get('hasta')
    if desde:
        pacientes = pacientes.filter(created_at__gte=desde)
    if hasta:
        pacientes = pacientes.filter(created_at__lte=hasta)
    
    # Filtro por sexo
    sexo = filtros.get('sexo')
    if sexo:
        pacientes = pacientes.filter(sexo=sexo)
    
    # Filtro por búsqueda de nombre
    busquedaNombre = filtros.get('busquedaNombre')
    if busquedaNombre:
        pacientes = pacientes.filter(
            Q(nombres__icontains=busquedaNombre) | 
            Q(apellidos__icontains=busquedaNombre)
        )
    
    # Convertir a lista para aplicar filtro de edad
    pacientes_lista = list(pacientes)
    
    # Filtro por rango de edad
    rangoEdad = filtros.get('rangoEdad')
    if rangoEdad:
        pacientes_filtrados = []
        for paciente in pacientes_lista:
            edad = calcular_edad(paciente.fecha_nacimiento)
            if rangoEdad == '0-18' and 0 <= edad <= 18:
                pacientes_filtrados.append(paciente)
            elif rangoEdad == '19-35' and 19 <= edad <= 35:
                pacientes_filtrados.append(paciente)
            elif rangoEdad == '36-50' and 36 <= edad <= 50:
                pacientes_filtrados.append(paciente)
            elif rangoEdad == '51-65' and 51 <= edad <= 65:
                pacientes_filtrados.append(paciente)
            elif rangoEdad == '65+' and edad >= 65:
                pacientes_filtrados.append(paciente)
        pacientes_lista = pacientes_filtrados
    
    # Preparar datos del reporte
    reporte = {
        'fecha_generacion': datetime.now().isoformat(),
        'total_pacientes': len(pacientes_lista),
        'filtros_aplicados': filtros,
        'pacientes': []
    }
    
    for paciente in pacientes_lista:
        edad = calcular_edad(paciente.fecha_nacimiento)
        reporte['pacientes'].append({
            'id': paciente.id,
            'nombres': paciente.nombres,
            'apellidos': paciente.apellidos,
            'nombre_completo': paciente.nombre_completo,
            'dui': paciente.dui or '',
            'fecha_nacimiento': paciente.fecha_nacimiento.isoformat(),
            'edad': edad,
            'sexo': paciente.get_sexo_display() if paciente.sexo else '',
            'telefono': paciente.telefono,
            'celular': paciente.celular or '',
            'email': paciente.email or '',
            'direccion': paciente.direccion or '',
            'fecha_registro': paciente.created_at.date().isoformat() if paciente.created_at else '',
        })
    
    return reporte

def imprimir_reporte(reporte):
    """Imprime el reporte en formato legible"""
    print("=" * 80)
    print("REPORTE DE PACIENTES")
    print("=" * 80)
    print(f"Fecha de generación: {reporte['fecha_generacion']}")
    print(f"Total de pacientes: {reporte['total_pacientes']}")
    
    if reporte['filtros_aplicados']:
        print("\nFiltros aplicados:")
        for key, value in reporte['filtros_aplicados'].items():
            if value:
                print(f"  - {key}: {value}")
    
    print("\n" + "=" * 80)
    print("LISTADO DE PACIENTES")
    print("=" * 80)
    
    for i, paciente in enumerate(reporte['pacientes'], 1):
        print(f"\n{i}. {paciente['nombre_completo']}")
        print(f"   DUI: {paciente['dui'] or 'N/A'}")
        print(f"   Edad: {paciente['edad']} años")
        print(f"   Sexo: {paciente['sexo']}")
        print(f"   Teléfono: {paciente['telefono']}")
        if paciente['celular']:
            print(f"   Celular: {paciente['celular']}")
        if paciente['email']:
            print(f"   Email: {paciente['email']}")
        print(f"   Fecha de registro: {paciente['fecha_registro']}")
    
    print("\n" + "=" * 80)

if __name__ == '__main__':
    # Generar reporte sin filtros (todos los pacientes)
    print("Generando reporte de pacientes...\n")
    reporte = generar_reporte_pacientes()
    imprimir_reporte(reporte)
    
    # Guardar reporte en JSON
    with open('reporte_pacientes.json', 'w', encoding='utf-8') as f:
        json.dump(reporte, f, ensure_ascii=False, indent=2)
    print("\nReporte guardado en: reporte_pacientes.json")
    
    # Ejemplo con filtros
    print("\n\n" + "=" * 80)
    print("EJEMPLO: Reporte filtrado (solo mujeres)")
    print("=" * 80)
    reporte_filtrado = generar_reporte_pacientes({'sexo': 'F'})
    print(f"Total de pacientes (mujeres): {reporte_filtrado['total_pacientes']}")

