from rest_framework.routers import DefaultRouter

from .views import (
	ExpedienteViewSet,
	FichaOrtodonciaViewSet,
	NotaProgresoOrtoViewSet,
	OdontogramaViewSet,
	OdontogramaVersionViewSet,
)


router = DefaultRouter()
router.register("expedientes", ExpedienteViewSet, basename="expedientes")
router.register(
	"fichas-ortodoncia", FichaOrtodonciaViewSet, basename="fichas-ortodoncia"
)
router.register("notas-progreso", NotaProgresoOrtoViewSet, basename="notas-progreso")
router.register("odontogramas", OdontogramaViewSet, basename="odontogramas")
router.register(
	"odontograma-versiones",
	OdontogramaVersionViewSet,
	basename="odontograma-versiones",
)


urlpatterns = router.urls
