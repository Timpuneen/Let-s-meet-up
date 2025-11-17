"""Configuration for the geography app."""

from django.apps import AppConfig


class GeographyConfig(AppConfig):
    """
    Django app configuration for the geography application.
    
    Handles configuration for country and city models.
    """
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.geography'
    verbose_name = 'Geography'
