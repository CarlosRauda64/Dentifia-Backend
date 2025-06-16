from django.urls import path, re_path
from rest_framework import routers
from . import views
from rest_framework_simplejwt.views import(
    TokenRefreshView,
)

router = routers.DefaultRouter()

router.register('api_usuarios', views.UsuarioViewSet, basename='usuarios')

urlpatterns = [
    path('login', views.login),
    path('crear', views.crear),
    path('editar/<int:id>', views.editar_usuario),
    path('profile', views.profile),
    path('listar_usuarios', views.listar_usuarios),
    path('token', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
]

urlpatterns += router.urls