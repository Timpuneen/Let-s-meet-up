from django.apps import AppConfig


class ParticipantsConfig(AppConfig):
    """
    Django app configuration for the participants application.
    
    Handles configuration for event participation management.
    """
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.participants'
    verbose_name = 'Participants'