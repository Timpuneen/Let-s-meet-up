"""Configuration for the comments app."""

from django.apps import AppConfig


class CommentsConfig(AppConfig):
    """
    Django app configuration for the comments application.
    
    Handles configuration for event comments and discussions.
    """
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'comments'
    verbose_name = 'Comments'