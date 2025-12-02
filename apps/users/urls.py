from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import AuthViewSet, CustomTokenRefreshView

app_name = 'users'

router = DefaultRouter()
router.register(r'', AuthViewSet, basename='auth')

urlpatterns = [
    # JWT token refresh endpoint
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    
    # POST /api/auth/signup/
    # POST /api/auth/login/
    # GET  /api/auth/me/
    path('', include(router.urls)),
]
