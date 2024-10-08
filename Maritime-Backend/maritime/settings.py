"""
Django settings for maritime project.

Generated by 'django-admin startproject' using Django 5.0.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path
import os
from django.utils.translation import gettext_lazy as _
from .utils import read_json
from .settings_local import *

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/


ALLOWED_HOSTS = ["localhost", "0.0.0.0", "127.0.0.1",]

CORS_ALLOWED_ORIGINS = [
"http://localhost:8080",
"http://127.0.0.1:8080"
]

CORS_ALLOW_ALL_ORIGINS = True # If this is used then `CORS_ALLOWED_ORIGINS` will not have any effect

NON_MANAGED_APPS= [app["name"] for app in APPS_LOCAL if not app["managed"]]

APPS = [
    "default",
    *[app["name"] for app in APPS_LOCAL if app["managed"]]
]

# Application definition
PROJECTS = [
    'maritime.abstract.apps.AbstractConfig',
    *[f"apps.{app['name']}.apps.{app['config']}" for app in APPS_LOCAL]
    ]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

ADDONS = [
    'rest_framework',
    'rest_framework_gis',
    'django_filters',
    'django.contrib.gis',
    'corsheaders',
    'drf_generators',
    # 'django_cleanup.apps.CleanupConfig',
    # 'polymorphic',
    # 'leaflet',
    'leaflet_admin_list',
    'admin_auto_filters',
    'rangefilter',
    'rest_framework_xml',
]

INSTALLED_APPS = [
    *PROJECTS,
    *ADDONS,

    "admin_interface",
    "colorfield",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'ckeditor',
    'leaflet',
    'mapwidgets'
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
]

ROOT_URLCONF = "maritime.urls"

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(str(BASE_DIR))],
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
WSGI_APPLICATION = "maritime.wsgi.application"

X_FRAME_OPTIONS = "SAMEORIGIN"
SILENCED_SYSTEM_CHECKS = ["security.W019"]

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASE_ROUTERS = ['maritime.routers.DjangoRouter', 'maritime.routers.AppRouter']


DATABASES = {name: read_json(os.path.join(str(BASE_DIR), 'configs', name, 'db.json')) for name in APPS+NON_MANAGED_APPS}



# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = [os.path.join(BASE_DIR, 'locale')]

LANGUAGES = [
    ('en', _('English')),
    ('sv', _('Swedish')),
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "static/"

STATIC_ROOT = os.path.join(BASE_DIR, 'static_build')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],
    'DEFAULT_METADATA_CLASS': 'rest_framework.metadata.SimpleMetadata',
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    # 'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    # 'DEFAULT_SCHEMA_CLASS': 'maritime.abstract.schemas.MaritimeSchema',
    'DEFAULT_PARSER_CLASSES': ['rest_framework_xml.parsers.XMLParser',],
    'DEFAULT_RENDERER_CLASSES': ['rest_framework_xml.renderers.XMLRenderer',],

}

MAP_WIDGETS = {
    "Leaflet": {
        "PointField": {
            "interactive": {
                "mapOptions": {
                    "zoom": 5,
                    "scrollWheelZoom": True,
                    "center": (57.124093162383616, 7.830100815389867),
                },
                "tileLayer": {
                "urlTemplate": "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
                "options": {"maxZoom": 20},
            },
            }
        },
        "markerFitZoom": 14,
    }
}