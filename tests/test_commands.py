"""
Tests for management commands.
"""

import json
import os
from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError


class TestApidogCommand:
    """Tests for the apidog management command."""

    def test_help_command(self):
        """Test that help is shown when no subcommand is given."""
        out = StringIO()
        call_command("apidog", stdout=out)
        output = out.getvalue()
        # Should show help without error
        assert "apidog" in output.lower() or output == ""

    def test_export_command(self, mock_apidog_settings, temp_output_dir):
        """Test export subcommand."""
        out = StringIO()
        call_command("apidog", "export", stdout=out)
        output = out.getvalue()

        # Check output messages
        assert "Schema exported" in output or "Fetching" in output

        # Check files created
        latest_file = os.path.join(temp_output_dir, "openapi_schema_latest.json")
        assert os.path.exists(latest_file)

        # Verify JSON content
        with open(latest_file) as f:
            schema = json.load(f)
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema

    def test_export_yaml_format(self, mock_apidog_settings, temp_output_dir):
        """Test export with YAML format."""
        out = StringIO()
        call_command("apidog", "export", "--format", "yaml", stdout=out)

        # Check YAML file created
        latest_file = os.path.join(temp_output_dir, "openapi_schema_latest.yaml")
        assert os.path.exists(latest_file)

    def test_export_custom_filename(self, mock_apidog_settings, temp_output_dir):
        """Test export with custom filename."""
        out = StringIO()
        call_command("apidog", "export", "--filename", "custom.json", stdout=out)

        # Check custom file created
        custom_file = os.path.join(temp_output_dir, "custom.json")
        assert os.path.exists(custom_file)

    def test_validate_command(self, mock_apidog_settings, temp_output_dir):
        """Test validate subcommand."""
        # First export
        call_command("apidog", "export", stdout=StringIO())

        # Then validate
        out = StringIO()
        call_command("apidog", "validate", stdout=out)
        output = out.getvalue()

        assert "valid" in output.lower()

    def test_validate_missing_file(self, mock_apidog_settings, temp_output_dir):
        """Test validate with missing file."""
        with pytest.raises(CommandError) as exc_info:
            call_command("apidog", "validate", "--file", "/nonexistent/file.json")

        assert "not found" in str(exc_info.value).lower()

    def test_env_config_command(self, mock_apidog_settings, temp_output_dir):
        """Test env-config subcommand."""
        out = StringIO()
        call_command("apidog", "env-config", stdout=out)
        output = out.getvalue()

        assert "Config saved" in output

        # Check file created
        config_file = os.path.join(temp_output_dir, "apidog_environments.json")
        assert os.path.exists(config_file)

        # Verify content
        with open(config_file) as f:
            config = json.load(f)
        assert "local" in config

    def test_init_command(self, mock_apidog_settings, temp_output_dir):
        """Test init subcommand."""
        out = StringIO()
        call_command("apidog", "init", stdout=out)
        output = out.getvalue()

        assert "initialization complete" in output.lower() or "APIDAG" in output

        # Check README created in output directory
        readme_file = os.path.join(temp_output_dir, "README.md")
        assert os.path.exists(readme_file)

    def test_push_without_credentials(self, mock_apidog_settings, temp_output_dir, monkeypatch):
        """Test push without credentials raises error."""
        # Clear credentials
        from ennam_django_apidog.settings import apidog_settings
        monkeypatch.setattr(apidog_settings, "PROJECT_ID", None)
        monkeypatch.setattr(apidog_settings, "TOKEN", None)

        with pytest.raises(CommandError) as exc_info:
            call_command("apidog", "push")

        assert "credentials required" in str(exc_info.value).lower()

    def test_pull_without_credentials(self, mock_apidog_settings, temp_output_dir, monkeypatch):
        """Test pull without credentials raises error."""
        from ennam_django_apidog.settings import apidog_settings
        monkeypatch.setattr(apidog_settings, "PROJECT_ID", None)
        monkeypatch.setattr(apidog_settings, "TOKEN", None)

        with pytest.raises(CommandError) as exc_info:
            call_command("apidog", "pull")

        assert "credentials required" in str(exc_info.value).lower()


class TestSchemaContent:
    """Tests for exported schema content."""

    def test_schema_has_metadata(self, mock_apidog_settings, temp_output_dir):
        """Test that exported schema has metadata."""
        call_command("apidog", "export", stdout=StringIO())

        latest_file = os.path.join(temp_output_dir, "openapi_schema_latest.json")
        with open(latest_file) as f:
            schema = json.load(f)

        # Check metadata
        assert "x-generated-by" in schema["info"]
        assert schema["info"]["x-generated-by"] == "ennam-django-apidog"
        assert "x-generated-at" in schema["info"]

    def test_schema_has_test_endpoint(self, mock_apidog_settings, temp_output_dir):
        """Test that schema includes test endpoint."""
        call_command("apidog", "export", stdout=StringIO())

        latest_file = os.path.join(temp_output_dir, "openapi_schema_latest.json")
        with open(latest_file) as f:
            schema = json.load(f)

        # Should have the test endpoint
        assert "/api/test/" in schema["paths"]
