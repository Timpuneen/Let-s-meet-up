"""Configuration for the media app."""

from django.apps import AppConfig


class MediaConfig(AppConfig):
    """
    Django app configuration for the media application.
    
    Handles configuration for event photos and media management.
    """
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'media'
    verbose_name = 'Media'