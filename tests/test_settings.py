"""
Tests for settings module.
"""


import pytest


class TestApidogSettings:
    """Tests for ApidogSettings class."""

    def test_default_settings(self):
        """Test that default settings are loaded."""
        from ennam_django_apidog.settings import apidog_settings

        assert apidog_settings.SCHEMA_ENDPOINT == "/api/schema/"
        assert apidog_settings.API_VERSION == "2024-03-28"
        assert apidog_settings.TIMEOUT == 60

    def test_user_settings_override(self, mock_apidog_settings):
        """Test that user settings override defaults."""
        from ennam_django_apidog.settings import apidog_settings

        apidog_settings.reload()
        assert apidog_settings.PROJECT_ID == "test-project-id"
        assert apidog_settings.TOKEN == "test-token"

    def test_environment_variable_override(self, monkeypatch, mock_apidog_settings):
        """Test that environment variables override defaults."""
        from ennam_django_apidog.settings import apidog_settings

        # Test with environment variables
        monkeypatch.setenv("APIDOG_PROJECT_ID", "env-project-id")
        monkeypatch.setenv("APIDOG_TOKEN", "env-token")
        apidog_settings.reload()

        # Mock fixture provides Django settings, env vars take precedence
        project_id, token = apidog_settings.get_credentials()
        assert project_id is not None
        assert token is not None

    def test_get_credentials(self, mock_apidog_settings):
        """Test get_credentials method."""
        from ennam_django_apidog.settings import apidog_settings

        apidog_settings.reload()

        # From settings
        project_id, token = apidog_settings.get_credentials()
        assert project_id == "test-project-id"
        assert token == "test-token"

        # With overrides
        project_id, token = apidog_settings.get_credentials("override-id", "override-token")
        assert project_id == "override-id"
        assert token == "override-token"

    def test_get_output_dir(self, mock_apidog_settings, temp_output_dir):
        """Test get_output_dir method."""
        from ennam_django_apidog.settings import apidog_settings

        apidog_settings.reload()
        output_dir = apidog_settings.get_output_dir()
        assert output_dir == temp_output_dir

    def test_invalid_setting_raises_error(self):
        """Test that accessing invalid setting raises AttributeError."""
        from ennam_django_apidog.settings import apidog_settings

        with pytest.raises(AttributeError):
            _ = apidog_settings.INVALID_SETTING

    def test_reload_clears_cache(self, mock_apidog_settings):
        """Test that reload clears cached values."""
        from ennam_django_apidog.settings import apidog_settings

        # Access a setting to cache it
        _ = apidog_settings.PROJECT_ID
        assert "PROJECT_ID" in apidog_settings._cached_attrs

        # Reload
        apidog_settings.reload()
        assert len(apidog_settings._cached_attrs) == 0
