"""Configuration for the friendships app."""

from django.apps import AppConfig


class FriendshipsConfig(AppConfig):
    """
    Django app configuration for the friendships application.
    
    Handles configuration for friendship management.
    """
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'friendships'
    verbose_name = 'Friendships'