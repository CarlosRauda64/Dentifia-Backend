from rest_framework import viewsets, filters, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Paciente
from .serializers import PacienteSerializer, PacienteCreateSerializer, PacienteListSerializer, DatosMedicosSerializer

class PacienteViewSet(viewsets.ModelViewSet):
    queryset = Paciente.objects.all()
    serializer_class = PacienteSerializer
    permission_classes = [permissions.IsAuthenticated]
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