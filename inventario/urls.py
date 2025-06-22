from django.urls import path, include
from rest_framework import routers
from .views import InsumoViewSet, MovimientoStockViewSet
from inventario import views

router = routers.DefaultRouter()
router.register('insumos', InsumoViewSet)
router.register('movimientos_stock', MovimientoStockViewSet)

urlpatterns = router.urls

urlpatterns += [
    path('movimiento_stock/eliminar/<int:id>/',views.eliminar_movimiento, name='eliminar_movimiento_stock'),
    path('movimiento_stock/insertar/', views.insertar_movimiento, name='insertar_movimiento_stock'),
    path('movimiento_stock/actualizar/<int:id>/', views.actualizar_movimiento, name='actualizar_movimiento_stock'),
]