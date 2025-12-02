from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import EventInvitationViewSet

app_name = 'invitations'

router = DefaultRouter()
router.register(r'', EventInvitationViewSet, basename='invitation')

urlpatterns = [
    path('', include(router.urls)),
]