import os
from django.core.wsgi import get_wsgi_application

from settings.conf import ENV_ID, ENV_POSSIBLE_OPTIONS

assert ENV_ID in ENV_POSSIBLE_OPTIONS, (
    f"Invalid MEETUP_ENV_ID: '{ENV_ID}'. "
    f"Must be one of {ENV_POSSIBLE_OPTIONS}"
)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.base')

application = get_wsgi_application()
