"""
Django settings for testing ennam-django-apidog.
"""

import os

SECRET_KEY = "test-secret-key-for-testing-only-do-not-use-in-production"
DEBUG = True

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "rest_framework",
    "drf_spectacular",
    "ennam_django_apidog",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

ROOT_URLCONF = "tests.urls"

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Test API",
    "DESCRIPTION": "API for testing",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

APIDOG_SETTINGS = {
    "OUTPUT_DIR": os.path.join(os.path.dirname(__file__), "test_output"),
    "SCHEMA_ENDPOINT": "/api/schema/",
    "PROJECT_ID": "test-project-id",
    "TOKEN": "test-token",
    "ENVIRONMENTS": {
        "local": {
            "name": "Local Development",
            "base_url": "http://localhost:8000",
        },
        "production": {
            "name": "Production",
            "base_url": "https://api.test.com",
        },
    },
}

# Minimal settings
USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
