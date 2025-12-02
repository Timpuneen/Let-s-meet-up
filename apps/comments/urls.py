from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CommentViewSet

app_name = 'comments'

router = DefaultRouter()
router.register(r'', CommentViewSet, basename='comment')

urlpatterns = [
    # GET    /api/comments/              - List comments
    # POST   /api/comments/              - Create comment
    # GET    /api/comments/{id}/         - Get comment details
    # PATCH  /api/comments/{id}/         - Update comment
    # DELETE /api/comments/{id}/         - Delete comment
    # GET    /api/comments/{id}/replies/ - Get nested replies
    path('', include(router.urls)),
]

