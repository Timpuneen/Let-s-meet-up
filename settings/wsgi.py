"""
WSGI config for Let's Meet Up project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

# Import environment configuration to get ENV_ID
from settings.conf import ENV_ID, ENV_POSSIBLE_OPTIONS

# Validate environment ID
assert ENV_ID in ENV_POSSIBLE_OPTIONS, (
    f"Invalid MEETUP_ENV_ID: '{ENV_ID}'. "
    f"Must be one of {ENV_POSSIBLE_OPTIONS}"
)

# Set Django settings module based on environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.base')

application = get_wsgi_application()
