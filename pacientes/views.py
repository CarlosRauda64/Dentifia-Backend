from rest_framework import viewsets, filters, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Paciente
from .serializers import PacienteSerializer, PacienteCreateSerializer, PacienteListSerializer, DatosMedicosSerializer


class IsDoctorOrReadOnly(permissions.BasePermission):
    """
    Permiso personalizado: Solo doctores y administradores pueden crear/editar/eliminar.
    Secretarias, doctores y administradores pueden leer.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Lecturas permitidas para doctor, secretaria y administrador
        if request.method in permissions.SAFE_METHODS:
            return request.user.rol in ['doctor', 'secretaria', 'administrador']
        
        # Escritura solo para doctor y administrador
        return request.user.rol in ['doctor', 'administrador']

class PacienteViewSet(viewsets.ModelViewSet):
    queryset = Paciente.objects.all()
    serializer_class = PacienteSerializer
    permission_classes = [IsDoctorOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # Filtros específicos
    filterset_fields = ['activo', 'sexo']
    
    # Búsqueda por múltiples campos
    search_fields = ['nombres', 'apellidos', 'dui', 'telefono', 'celular', 'email']
    
    # Ordenamiento por defecto
    ordering_fields = ['nombres', 'apellidos', 'created_at', 'fecha_nacimiento']
    ordering = ['-created_at']
    
    # Paginación
    pagination_class = PageNumberPagination
    page_size = 20
    
    def get_serializer_class(self):
        """Usar serializer específico según la acción"""
        if self.action == 'list':
            return PacienteListSerializer
        elif self.action == 'create':
            return PacienteCreateSerializer
        return PacienteSerializer
    
    def get_queryset(self):
        """Filtrar pacientes activos por defecto"""
        queryset = Paciente.objects.all()
        
        # Filtro por activo (por defecto solo activos)
        activo = self.request.query_params.get('activo', 'true')
        if activo.lower() == 'true':
            queryset = queryset.filter(activo=True)
        elif activo.lower() == 'false':
            queryset = queryset.filter(activo=False)
        
        return queryset
    
    @action(detail=True, methods=['patch'])
    def actualizar_datos_medicos(self, request, pk=None):
        """Endpoint específico para actualizar solo datos médicos"""
        paciente = self.get_object()
        datos_medicos_serializer = DatosMedicosSerializer(data=request.data)
        
        if datos_medicos_serializer.is_valid():
            paciente.datos_medicos.update(datos_medicos_serializer.validated_data)
            paciente.save()
            return Response({'message': 'Datos médicos actualizados correctamente'})
        return Response(datos_medicos_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def buscar(self, request):
        """Búsqueda avanzada de pacientes"""
        query = request.query_params.get('q', '')
        if query:
            queryset = self.get_queryset().filter(
                Q(nombres__icontains=query) |
                Q(apellidos__icontains=query) |
                Q(dui__icontains=query) |
                Q(telefono__icontains=query) |
                Q(celular__icontains=query)
            )
            serializer = PacienteListSerializer(queryset, many=True)
            return Response(serializer.data)
        return Response([])
    
    @action(detail=False, methods=['get'])
    def busqueda_rapida(self, request):
        """Búsqueda rápida para autocompletado (nombre, apellido, DUI)"""
        query = request.query_params.get('q', '')
        if len(query) >= 2:  # Mínimo 2 caracteres
            pacientes = self.get_queryset().filter(
                Q(nombres__icontains=query) |
                Q(apellidos__icontains=query) |
                Q(dui__icontains=query)
            )[:10]  # Limitar a 10 resultados
            serializer = PacienteListSerializer(pacientes, many=True)
            return Response(serializer.data)
        return Response([])

    def destroy(self, request, *args, **kwargs):
        """Borrado lógico del paciente con validación de dependencias"""
        paciente = self.get_object()

        # Validar que no tenga facturas asociadas
        if paciente.facturas.exists():
            return Response(
                {"error": "No es posible eliminar pacientes vinculados a facturas o tratamientos"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Borrado lógico
        paciente.activo = False
        paciente.save()

        return Response(
            {"message": "Paciente eliminado correctamente"},
            status=status.HTTP_200_OK
        )