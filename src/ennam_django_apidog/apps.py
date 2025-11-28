"""Django app configuration for ennam-django-apidog."""

from django.apps import AppConfig


class ApidogConfig(AppConfig):
    """Configuration for the APIDOG Django app."""

    name = "ennam_django_apidog"
    verbose_name = "APIDOG Integration"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        """Perform initialization when the app is ready."""
        # Import settings to validate configuration on startup
        pass
