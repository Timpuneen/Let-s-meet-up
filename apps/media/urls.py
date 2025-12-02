from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PhotoViewSet

app_name = 'media'

router = DefaultRouter()
router.register(r'', PhotoViewSet, basename='photo')

urlpatterns = [
    # GET    /api/photos/                   - List photos (with filtering)
    # POST   /api/photos/                   - Upload photo
    # GET    /api/photos/{id}/              - Get photo details
    # PATCH  /api/photos/{id}/              - Update photo
    # DELETE /api/photos/{id}/              - Delete photo
    # POST   /api/photos/{id}/set_cover/    - Set as cover photo
    # POST   /api/photos/{id}/remove_cover/ - Remove cover status
    path('', include(router.urls)),
]

