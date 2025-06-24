from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FacturaViewSet
from .views import FacturaViewSet, DetalleFacturaViewSet


router = DefaultRouter()
router.register(r'facturas', FacturaViewSet, basename='factura')
router.register(r'detalles', DetalleFacturaViewSet, basename='detallefactura')


urlpatterns = [
    path('', include(router.urls)),
]
