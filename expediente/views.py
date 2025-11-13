from django.db import transaction
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
	Expediente,
	FichaOrtodoncia,
	NotaProgresoOrto,
	Odontograma,
	OdontogramaVersion,
)
from .serializers import (
	ExpedienteDetailSerializer,
	ExpedienteSerializer,
	FichaOrtodonciaSerializer,
	NotaProgresoOrtoSerializer,
	OdontogramaSerializer,
	OdontogramaVersionCreateSerializer,
	OdontogramaVersionSerializer,
)


class ExpedienteViewSet(viewsets.ModelViewSet):
	queryset = (
		Expediente.objects.select_related("paciente")
		.prefetch_related(
			"fichas_ortodoncia__notas_progreso",
			"odontograma__versiones__detalles",
		)
		.order_by("-created_at")
	)
	permission_classes = [permissions.IsAuthenticated]
	filter_backends = [DjangoFilterBackend, filters.SearchFilter]
	filterset_fields = ["paciente"]
	search_fields = [
		"numero_expediente",
		"paciente__nombres",
		"paciente__apellidos",
	]
	http_method_names = ["get", "post", "put", "patch", "delete", "head", "options"]

	def get_serializer_class(self):
		if self.action == "retrieve":
			return ExpedienteDetailSerializer
		if self.action == "list" and self.request.query_params.get("expand") == "full":
			return ExpedienteDetailSerializer
		return ExpedienteSerializer

	def perform_create(self, serializer):
		expediente = serializer.save()
		Odontograma.objects.get_or_create(expediente=expediente)


class FichaOrtodonciaViewSet(viewsets.ModelViewSet):
	queryset = (
		FichaOrtodoncia.objects.select_related("expediente", "expediente__paciente")
		.prefetch_related("notas_progreso")
		.order_by("-created_at")
	)
	serializer_class = FichaOrtodonciaSerializer
	permission_classes = [permissions.IsAuthenticated]
	filter_backends = [DjangoFilterBackend, filters.SearchFilter]
	filterset_fields = ["expediente", "estado_tratamiento"]
	search_fields = ["expediente__numero_expediente", "diagnostico", "plan_tratamiento"]
	http_method_names = ["get", "post", "put", "patch", "delete", "head", "options"]


class NotaProgresoOrtoViewSet(viewsets.ModelViewSet):
	queryset = (
		NotaProgresoOrto.objects.select_related(
			"ficha_ortodoncia",
			"ficha_ortodoncia__expediente",
			"ficha_ortodoncia__expediente__paciente",
		)
		.order_by("-created_at")
	)
	serializer_class = NotaProgresoOrtoSerializer
	permission_classes = [permissions.IsAuthenticated]
	filter_backends = [DjangoFilterBackend, filters.SearchFilter]
	filterset_fields = ["ficha_ortodoncia"]
	search_fields = ["motivo_visita", "observaciones_clinicas", "procedimiento_realizado"]
	http_method_names = ["get", "post", "put", "patch", "delete", "head", "options"]


class OdontogramaViewSet(viewsets.ReadOnlyModelViewSet):
	queryset = (
		Odontograma.objects.select_related("expediente", "expediente__paciente")
		.prefetch_related("versiones__detalles")
		.order_by("-created_at")
	)
	serializer_class = OdontogramaSerializer
	permission_classes = [permissions.IsAuthenticated]
	filter_backends = [DjangoFilterBackend]
	filterset_fields = ["expediente"]
	http_method_names = ["get", "head", "options"]

	@action(detail=False, methods=["get"], url_path="por-expediente/(?P<expediente_id>[^/.]+)")
	def por_expediente(self, request, expediente_id=None):
		odontograma = self.get_queryset().filter(expediente_id=expediente_id).first()
		if not odontograma:
			return Response(status=status.HTTP_404_NOT_FOUND)
		serializer = self.get_serializer(odontograma)
		return Response(serializer.data)


class OdontogramaVersionViewSet(viewsets.ModelViewSet):
	queryset = (
		OdontogramaVersion.objects.select_related(
			"odontograma",
			"odontograma__expediente",
			"odontograma__expediente__paciente",
		)
		.prefetch_related("detalles")
		.order_by("-created_at")
	)
	permission_classes = [permissions.IsAuthenticated]
	filter_backends = [DjangoFilterBackend]
	filterset_fields = ["odontograma"]
	http_method_names = ["get", "post", "delete", "head", "options"]

	def get_serializer_class(self):
		if self.action == "create":
			return OdontogramaVersionCreateSerializer
		return OdontogramaVersionSerializer

	@transaction.atomic
	def perform_create(self, serializer):
		serializer.save()
