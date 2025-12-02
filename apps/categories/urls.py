from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet

app_name = 'categories'

router = DefaultRouter()
router.register(r'', CategoryViewSet, basename='category')


urlpatterns = [
    # Category CRUD endpoints
    path('', include(router.urls)),
]
