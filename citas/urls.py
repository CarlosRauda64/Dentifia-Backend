from django.urls import path, include
from rest_framework import routers
from .views import CitaViewSet
from citas import views

router = routers.DefaultRouter()
router.register(r'', CitaViewSet, basename='cita')

urlpatterns = [
    path('', include(router.urls)),
    path('listar/', views.listar_citas, name='listar_citas'),
    path('insertar/', views.insertar_cita, name='insertar_cita'),
    path('eliminar/<int:cita_id>/', views.eliminar_cita, name='eliminar_cita'),
]
