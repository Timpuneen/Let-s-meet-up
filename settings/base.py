"""
Base settings for Let's Meet Up project.

This module contains all environment-agnostic settings that are shared
between local and production environments.
"""

from datetime import timedelta
from settings.conf import BASE_DIR, SECRET_KEY

# SECRET_KEY imported from conf.py
# BASE_DIR imported from conf.py

# Root URL configuration
ROOT_URLCONF = 'settings.urls'

# WSGI/ASGI applications
WSGI_APPLICATION = 'settings.wsgi.application'
ASGI_APPLICATION = 'settings.asgi.application'

# Application definition
INSTALLED_APPS = [
    # Unfold must come before django.contrib.admin
    'unfold',
    'unfold.contrib.filters',
    'unfold.contrib.forms',
    'unfold.contrib.import_export',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'drf_spectacular',
    'import_export',

    # Local apps
    'apps.core',
    'apps.abstracts',
    'apps.users',
    'apps.events',
    'apps.geography',
    'apps.friendships',
    'apps.categories',
    'apps.participants',
    'apps.media',
    'apps.comments',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Almaty'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files (User uploads)
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom user model
AUTH_USER_MODEL = 'users.User'

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# JWT settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# Django Unfold settings (Admin UI)
# Django Unfold settings (Admin UI)
UNFOLD = {
    "SITE_TITLE": "Let's Meet Up",
    "SITE_HEADER": "Let's Meet Up Administration",
    "SITE_URL": "/",
    "SITE_ICON": {
        "light": lambda request: "https://img.icons8.com/fluency/48/calendar.png",
        "dark": lambda request: "https://img.icons8.com/fluency/48/calendar.png",
    },
    "SITE_LOGO": {
        "light": lambda request: "https://img.icons8.com/fluency/96/calendar.png",
        "dark": lambda request: "https://img.icons8.com/fluency/96/calendar.png",
    },
    "SITE_SYMBOL": "calendar_month",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "COLORS": {
        "primary": {
            "50": "250 245 255",
            "100": "243 232 255",
            "200": "233 213 255",
            "300": "216 180 254",
            "400": "192 132 252",
            "500": "168 85 247",
            "600": "147 51 234",
            "700": "126 34 206",
            "800": "107 33 168",
            "900": "88 28 135",
            "950": "59 7 100",
        },
    },
    "EXTENSIONS": {
        "modeltranslation": {
            "flags": {
                "en": "🇬🇧",
                "fr": "🇫🇷",
                "nl": "🇧🇪",
            },
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": "Dashboard",
                "separator": False,
                "collapsible": False,
                "items": [
                    {
                        "title": "Overview",
                        "icon": "dashboard",
                        "link": lambda request: "/admin/",
                    },
                ],
            },
            {
                "title": "Events Management",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Events",
                        "icon": "event",
                        "link": lambda request: "/admin/events/event/",
                        "badge": lambda request: Event.objects.filter(status='published').count() if 'Event' in globals() else 0,
                    },
                    {
                        "title": "Participants",
                        "icon": "group",
                        "link": lambda request: "/admin/participants/eventparticipant/",
                    },
                    {
                        "title": "Categories",
                        "icon": "category",
                        "link": lambda request: "/admin/categories/category/",
                    },
                    {
                        "title": "Comments",
                        "icon": "comment",
                        "link": lambda request: "/admin/comments/eventcomment/",
                    },
                    {
                        "title": "Photos",
                        "icon": "photo_library",
                        "link": lambda request: "/admin/media/eventphoto/",
                    },
                ],
            },
            {
                "title": "Users & Social",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Users",
                        "icon": "person",
                        "link": lambda request: "/admin/users/user/",
                        "badge": lambda request: User.objects.filter(is_active=True).count() if 'User' in globals() else 0,
                    },
                    {
                        "title": "Friendships",
                        "icon": "diversity_3",
                        "link": lambda request: "/admin/friendships/friendship/",
                    },
                ],
            },
            {
                "title": "Geography",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Countries",
                        "icon": "public",
                        "link": lambda request: "/admin/geography/country/",
                    },
                    {
                        "title": "Cities",
                        "icon": "location_city",
                        "link": lambda request: "/admin/geography/city/",
                    },
                ],
            },
            {
                "title": "System",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Groups",
                        "icon": "group",
                        "link": lambda request: "/admin/auth/group/",
                    },
                ],
            },
        ],
    },
    "TABS": [
        {
            "models": [
                "events.event",
            ],
            "items": [
                {
                    "title": "Event Details",
                    "link": lambda request, instance=None: f"/admin/events/event/{instance.pk}/change/" if instance else None,
                    "permission": lambda request: request.user.is_staff,
                },
                {
                    "title": "Participants",
                    "link": lambda request, instance=None: f"/admin/participants/eventparticipant/?event__id__exact={instance.pk}" if instance else None,
                },
                {
                    "title": "Comments",
                    "link": lambda request, instance=None: f"/admin/comments/eventcomment/?event__id__exact={instance.pk}" if instance else None,
                },
                {
                    "title": "Photos",
                    "link": lambda request, instance=None: f"/admin/media/eventphoto/?event__id__exact={instance.pk}" if instance else None,
                },
            ],
        },
        {
            "models": [
                "users.user",
            ],
            "items": [
                {
                    "title": "User Profile",
                    "link": lambda request, instance=None: f"/admin/users/user/{instance.pk}/change/" if instance else None,
                },
                {
                    "title": "Organized Events",
                    "link": lambda request, instance=None: f"/admin/events/event/?organizer__id__exact={instance.pk}" if instance else None,
                },
                {
                    "title": "Participations",
                    "link": lambda request, instance=None: f"/admin/participants/eventparticipant/?user__id__exact={instance.pk}" if instance else None,
                },
                {
                    "title": "Friendships",
                    "link": lambda request, instance=None: f"/admin/friendships/friendship/?sender__id__exact={instance.pk}" if instance else None,
                },
            ],
        },
    ],
}

# DRF Spectacular settings (Swagger/OpenAPI)
SPECTACULAR_SETTINGS = {
    'TITLE': "Let's Meet Up API",
    'DESCRIPTION': 'API for managing meetup events and user registrations',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,

    # Authentication
    'COMPONENT_SPLIT_REQUEST': True,
    'SECURITY': [{'Bearer': []}],
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'JWT Authorization header using the Bearer scheme. Example: "Bearer {token}"'
        }
    },

    # Schema generation
    'SCHEMA_PATH_PREFIX': r'/api/',
    'SCHEMA_PATH_PREFIX_TRIM': True,
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': True,
    },
    'SWAGGER_UI_FAVICON_HREF': 'https://img.icons8.com/fluency/48/calendar.png',

    # Tags
    'TAGS': [
        {'name': 'Authentication', 'description': 'User authentication endpoints'},
        {'name': 'Events', 'description': 'Event management and registration'},
    ],
}
