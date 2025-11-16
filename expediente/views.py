from django.db import transaction
from rest_framework import filters, permissions, status, viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
import cloudinary.api
from cloudinary import CloudinaryImage
import requests

from .models import (
	Expediente,
	FichaOrtodoncia,
	NotaProgresoOrto,
	Odontograma,
	OdontogramaVersion,
    Anexo,
)
from .serializers import (
	ExpedienteDetailSerializer,
	ExpedienteSerializer,
	FichaOrtodonciaSerializer,
	NotaProgresoOrtoSerializer,
	OdontogramaSerializer,
	OdontogramaVersionCreateSerializer,
	OdontogramaVersionSerializer,
    AnexoSerializer,
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


class AnexoViewSet(viewsets.ModelViewSet):
	queryset = Anexo.objects.select_related("expediente").order_by("-created_at")
	serializer_class = AnexoSerializer
	permission_classes = [permissions.IsAuthenticated]
	parser_classes = [MultiPartParser, FormParser]
	filter_backends = [DjangoFilterBackend, filters.SearchFilter]
	filterset_fields = ["expediente"]
	search_fields = ["nombre_original", "descripcion"]
	http_method_names = ["get", "post", "delete", "head", "options"]

	def perform_create(self, serializer):
		# If an uploaded file is present, ensure nombre_original is set from the file
		archivo = None
		if hasattr(self.request, "FILES"):
			archivo = self.request.FILES.get("archivo")
		# Prepare save kwargs
		save_kwargs = {}
		if archivo and not serializer.validated_data.get("nombre_original"):
			save_kwargs["nombre_original"] = getattr(archivo, "name", None)
		if hasattr(self.request, "user") and self.request.user and self.request.user.is_authenticated:
			save_kwargs["uploaded_by"] = self.request.user
		# Saving will use the field's storage (Cloudinary) because the FileField uses MediaCloudinaryStorage
		serializer.save(**save_kwargs)

	def create(self, request, *args, **kwargs):
		"""Override create to return a JSON error when an exception occurs (e.g., Cloudinary auth)."""
		try:
			return super().create(request, *args, **kwargs)
		except Exception as exc:
			# Return a JSON response with the error message instead of the Django debug HTML page
			return Response({"detail": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

	@action(detail=True, methods=["get"], permission_classes=[permissions.IsAuthenticated])
	def download_url(self, request, pk=None):
		"""Return a JSON object with the Cloudinary URL and a filename for the requested Anexo.

		This endpoint requires authentication. The frontend should call this endpoint with the
		user's bearer token, receive the URL in the JSON response, and then use that URL to
		open or download the file directly from Cloudinary (no Authorization header required
		when fetching the Cloudinary URL itself).
		"""
		anexo = self.get_object()
		url = None
		filename = anexo.nombre_original if getattr(anexo, "nombre_original", None) else None

		if getattr(anexo, "archivo", None):
			public_id = anexo.archivo.name
			# Try to detect resource info (type/format) to build a proper signed URL
			resource_type = "authenticated"
			fmt = None
			try:
				info = cloudinary.api.resource(public_id)
				# prefer 'resource_type' key, fallback to 'type'
				resource_type = info.get("resource_type") or info.get("type") or resource_type
				fmt = info.get("format")
			except Exception:
				# If API lookup fails, fall back to 'authenticated' and no format
				pass

			# Try several candidate types and validate the signed URL by doing a HEAD
			candidates = []
			tried_types = [resource_type, "authenticated", "private", "upload"]
			# choose resource_type for building URL: PDFs and raw resources need 'raw'
			options_base = {
				"resource_type": "raw" if (fmt == "pdf" or resource_type == "raw") else "auto",
				"secure": True,
				"sign_url": True,
			}
			if fmt and resource_type != "raw":
				# include explicit format for image/video resources
				options_base["format"] = fmt

			for t in tried_types:
				if not t:
					continue
				options = dict(options_base)
				options["type"] = t
				try:
					candidate = CloudinaryImage(public_id).build_url(**options)
					# Validate the candidate URL by requesting HEAD
					try:
						rs = requests.head(candidate, allow_redirects=True, timeout=10)
						if rs.status_code == 200:
							url = candidate
							break
						# some CDN responses may return 302 -> follow redirects above
					except Exception:
						# ignore validation errors and try next type
						continue
				except Exception:
					continue

			# If none validated, fallback to stored URL
			if not url:
				try:
					url = anexo.archivo.url
				except Exception:
					url = None

		return Response({"url": url, "filename": filename})


