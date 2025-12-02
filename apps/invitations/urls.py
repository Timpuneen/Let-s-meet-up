"""
URL configuration for invitations app.

This module defines URL patterns for event invitation endpoints.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import EventInvitationViewSet

app_name = 'invitations'

router = DefaultRouter()
router.register(r'invitations', EventInvitationViewSet, basename='invitation')

urlpatterns = [
    path('', include(router.urls)),
]