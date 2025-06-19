from django.urls import path, include
from rest_framework import routers
from .views import InsumoViewSet, MovimientoStockViewSet

router = routers.DefaultRouter()
router.register('insumos', InsumoViewSet)
router.register('movimientos-stock', MovimientoStockViewSet)

urlpatterns = router.urls