from django.urls import path, re_path
from . import views
from rest_framework_simplejwt.views import(
    TokenRefreshView,
)

urlpatterns = [
    path('login', views.login),
    path('crear', views.crear),
    path('profile', views.profile),
    path('listar_usuarios', views.listar_usuarios),
    path('token', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
]