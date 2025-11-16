"""Configuration for the categories app."""

from django.apps import AppConfig


class CategoriesConfig(AppConfig):
    """
    Django app configuration for the categories application.
    
    Handles configuration for event categorization.
    """
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'categories'
    verbose_name = 'Categories'