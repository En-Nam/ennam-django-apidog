"""
Settings configuration for ennam-django-apidog.

Usage in Django settings.py:

    APIDOG_SETTINGS = {
        'OUTPUT_DIR': '/path/to/apidog/',
        'SCHEMA_ENDPOINT': '/api/schema/',
        'PROJECT_ID': 'your-project-id',
        'TOKEN': 'your-api-token',
        'ENVIRONMENTS': {
            'production': {
                'name': 'Production',
                'base_url': 'https://api.yourapp.com',
            },
        },
    }
"""

import os
from django.conf import settings


DEFAULTS = {
    # Output configuration
    "OUTPUT_DIR": None,  # Default: <project_root>/apidog/
    "SCHEMA_ENDPOINT": "/api/schema/",

    # APIDOG Cloud configuration
    "PROJECT_ID": None,  # Can also use env var APIDOG_PROJECT_ID
    "TOKEN": None,  # Can also use env var APIDOG_TOKEN
    "API_VERSION": "2024-03-28",
    "API_BASE_URL": "https://api.apidog.com/v1",
    "TIMEOUT": 60,

    # Environment configurations for env-config command
    "ENVIRONMENTS": {
        "local": {
            "name": "Local Development",
            "base_url": "http://localhost:8000",
            "variables": {"AUTH_TOKEN": "", "API_VERSION": "v1"},
        },
        "development": {
            "name": "Development",
            "base_url": "",
            "variables": {"AUTH_TOKEN": "", "API_VERSION": "v1"},
        },
        "staging": {
            "name": "Staging",
            "base_url": "",
            "variables": {"AUTH_TOKEN": "", "API_VERSION": "v1"},
        },
        "production": {
            "name": "Production",
            "base_url": "",
            "variables": {"AUTH_TOKEN": "", "API_VERSION": "v1"},
        },
    },
}


class ApidogSettings:
    """
    A settings object that allows APIDOG settings to be accessed as properties.

    Settings are read from Django's settings.py under APIDOG_SETTINGS dict,
    with fallback to environment variables and defaults.

    Example:
        from ennam_django_apidog.settings import apidog_settings

        project_id = apidog_settings.PROJECT_ID
        output_dir = apidog_settings.OUTPUT_DIR
    """

    def __init__(self):
        self.defaults = DEFAULTS
        self._cached_attrs = set()

    @property
    def user_settings(self):
        """Get user-defined settings from Django settings."""
        if not hasattr(self, "_user_settings"):
            self._user_settings = getattr(settings, "APIDOG_SETTINGS", {})
        return self._user_settings

    def __getattr__(self, attr):
        if attr not in self.defaults:
            raise AttributeError(f"Invalid APIDOG setting: '{attr}'")

        # Check user settings first
        try:
            val = self.user_settings[attr]
        except KeyError:
            # Check environment variables for certain settings
            if attr == "PROJECT_ID":
                val = os.environ.get("APIDOG_PROJECT_ID", self.defaults[attr])
            elif attr == "TOKEN":
                val = os.environ.get("APIDOG_TOKEN", self.defaults[attr])
            elif attr == "OUTPUT_DIR":
                val = os.environ.get("APIDOG_OUTPUT_DIR", self.defaults[attr])
            else:
                val = self.defaults[attr]

        # Cache the value
        self._cached_attrs.add(attr)
        setattr(self, attr, val)
        return val

    def get_output_dir(self):
        """Get the output directory, creating it if necessary."""
        output_dir = self.OUTPUT_DIR

        if not output_dir:
            # Default to apidog/ at project root (parent of BASE_DIR)
            base_dir = getattr(settings, "BASE_DIR", os.getcwd())
            # If BASE_DIR is the app directory, go up one level
            if os.path.basename(base_dir) == "app":
                output_dir = os.path.join(os.path.dirname(base_dir), "apidog")
            else:
                output_dir = os.path.join(base_dir, "apidog")

        return output_dir

    def get_credentials(self, project_id=None, token=None):
        """
        Get APIDOG credentials, with command-line overrides.

        Args:
            project_id: Override from command line
            token: Override from command line

        Returns:
            tuple: (project_id, token)
        """
        pid = project_id or self.PROJECT_ID
        tok = token or self.TOKEN
        return pid, tok

    def reload(self):
        """Reload settings (useful for testing)."""
        for attr in self._cached_attrs:
            try:
                delattr(self, attr)
            except AttributeError:
                pass
        self._cached_attrs.clear()
        if hasattr(self, "_user_settings"):
            delattr(self, "_user_settings")


# Global settings instance
apidog_settings = ApidogSettings()
