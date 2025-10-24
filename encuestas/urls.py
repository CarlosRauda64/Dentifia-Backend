from django.urls import path, include
from rest_framework import routers
from .views import EncuestaViewSet
from encuestas import views

router = routers.DefaultRouter()
router.register('encuestas', EncuestaViewSet,basename='encuestas')

urlpatterns = router.urls

urlpatterns+=[
    path('listar', views.listar_encuestas, name='listar_encuestas'),
    path('insertar_encuesta/', views.insertar_encuesta, name='insertar_encuesta'),
    path('eliminar_encuesta/<int:encuesta_id>/', views.eliminar_encuesta, name='eliminar_encuesta'),
]