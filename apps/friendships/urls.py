"""
URL configuration for friendships app.

This module defines URL patterns for friendship endpoints.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import FriendshipViewSet

app_name = 'friendships'

router = DefaultRouter()
router.register(r'friendships', FriendshipViewSet, basename='friendship')

urlpatterns = [
    path('', include(router.urls)),
]

