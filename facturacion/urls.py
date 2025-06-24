from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import FacturaViewSet
from .views import FacturaViewSet, DetalleFacturaViewSet


router = DefaultRouter()
router.register(r'facturas', FacturaViewSet, basename='factura')
router.register(r'detalles', DetalleFacturaViewSet, basename='detallefactura')


urlpatterns = [
    path('', include(router.urls)),
    path('eliminar/<str:pk>/', views.eliminar_factura, name='eliminar_factura'),
]
