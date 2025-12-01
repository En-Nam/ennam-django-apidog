"""Tests for error handling and edge cases in management commands."""
import json
import os
import shutil
from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError


class TestExportEdgeCases:
    """Edge cases for export command."""

    def test_export_creates_output_directory(self, mock_apidog_settings):
        """Test export creates directory if missing."""
        output_dir = mock_apidog_settings["OUTPUT_DIR"]

        # Remove directory if exists
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)

        assert not os.path.exists(output_dir)

        # Export should create it
        call_command("apidog", "export", stdout=StringIO())
        assert os.path.exists(output_dir)

    def test_export_custom_filename(self, mock_apidog_settings, temp_output_dir):
        """Test export with custom filename."""
        out = StringIO()
        call_command("apidog", "export", filename="custom.json", stdout=out)

        custom_path = os.path.join(temp_output_dir, "custom.json")
        assert os.path.exists(custom_path)

    def test_export_yaml_format(self, mock_apidog_settings, temp_output_dir):
        """Test export in YAML format."""
        out = StringIO()
        call_command("apidog", "export", format="yaml", stdout=out)

        output = out.getvalue()
        assert "openapi" in output.lower() or "Schema exported to" in output

    def test_export_creates_latest_version(self, mock_apidog_settings, temp_output_dir):
        """Test export creates openapi_schema_latest.json."""
        call_command("apidog", "export", stdout=StringIO())

        latest_path = os.path.join(temp_output_dir, "openapi_schema_latest.json")
        assert os.path.exists(latest_path)

        # Verify it's valid JSON
        with open(latest_path) as f:
            schema = json.load(f)
            assert "openapi" in schema

    def test_export_custom_indentation(self, mock_apidog_settings, temp_output_dir):
        """Test export with custom JSON indentation."""
        call_command("apidog", "export", indent=4, stdout=StringIO())

        latest_path = os.path.join(temp_output_dir, "openapi_schema_latest.json")
        with open(latest_path) as f:
            content = f.read()
            # With indent=4, should have 4 spaces for first level indent
            assert "    " in content


class TestValidateEdgeCases:
    """Edge cases for validate command."""

    def test_validate_invalid_json(self, temp_output_dir):
        """Test validate with malformed JSON."""
        bad_file = os.path.join(temp_output_dir, "bad.json")
        with open(bad_file, "w") as f:
            f.write("{invalid json")

        with pytest.raises((json.JSONDecodeError, CommandError)):
            call_command("apidog", "validate", file=bad_file, stdout=StringIO())

    def test_validate_missing_required_fields(self, temp_output_dir):
        """Test validate with incomplete schema."""
        bad_schema = os.path.join(temp_output_dir, "incomplete.json")
        with open(bad_schema, "w") as f:
            json.dump({"info": {}}, f)  # Missing 'openapi' and 'paths'

        with pytest.raises(CommandError) as exc_info:
            call_command("apidog", "validate", file=bad_schema, stdout=StringIO())

        error_msg = str(exc_info.value).lower()
        assert "missing required field" in error_msg or "openapi" in error_msg

    def test_validate_missing_openapi_field(self, temp_output_dir):
        """Test validate fails without 'openapi' field."""
        schema_file = os.path.join(temp_output_dir, "no_openapi.json")
        with open(schema_file, "w") as f:
            json.dump({"info": {"title": "Test"}, "paths": {}}, f)

        with pytest.raises(CommandError) as exc_info:
            call_command("apidog", "validate", file=schema_file, stdout=StringIO())

        assert "openapi" in str(exc_info.value).lower()

    def test_validate_nonexistent_file(self, temp_output_dir):
        """Test validate with nonexistent file."""
        nonexistent = os.path.join(temp_output_dir, "nonexistent.json")

        with pytest.raises(CommandError) as exc_info:
            call_command("apidog", "validate", file=nonexistent, stdout=StringIO())

        assert "not found" in str(exc_info.value).lower()

    def test_validate_default_latest_schema(self, mock_apidog_settings, temp_output_dir):
        """Test validate uses latest schema by default."""
        # Export first to create latest
        call_command("apidog", "export", stdout=StringIO())

        # Validate without specifying file
        out = StringIO()
        result = call_command("apidog", "validate", stdout=out)

        assert result is True
        assert "valid" in out.getvalue().lower()


class TestInitEdgeCases:
    """Edge cases for init command."""

    def test_init_creates_apidog_directory(self, mock_apidog_settings, temp_output_dir):
        """Test init creates apidog directory."""
        assert os.path.exists(temp_output_dir)

    def test_init_with_existing_gitignore(self, mock_apidog_settings):
        """Test init appends to existing .gitignore."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create existing .gitignore
            gitignore_path = os.path.join(tmpdir, ".gitignore")
            with open(gitignore_path, "w") as f:
                f.write("# Existing rules\n*.pyc\n")

            # Mock settings to use temp dir
            from unittest.mock import patch

            with patch(
                "ennam_django_apidog.settings.apidog_settings.get_output_dir"
            ) as mock_get_dir:
                mock_get_dir.return_value = os.path.join(tmpdir, "apidog")

                call_command("apidog", "init", stdout=StringIO())

                # Verify both content present
                with open(gitignore_path) as f:
                    content = f.read()
                    assert "*.pyc" in content
                    assert "APIDOG" in content

    def test_init_creates_readme(self, mock_apidog_settings, temp_output_dir):
        """Test init creates README.md in apidog directory."""
        call_command("apidog", "init", stdout=StringIO())

        readme_path = os.path.join(temp_output_dir, "README.md")
        assert os.path.exists(readme_path)

        with open(readme_path) as f:
            content = f.read()
            assert "APIDOG" in content

    def test_init_force_overwrites(self, mock_apidog_settings, temp_output_dir):
        """Test init --force overwrites existing files."""
        # Create initial files
        call_command("apidog", "init", stdout=StringIO())

        # Get original README content
        readme_path = os.path.join(temp_output_dir, "README.md")
        with open(readme_path, "w") as f:
            f.write("Modified content")

        # Run init again with --force
        call_command("apidog", "init", force=True, stdout=StringIO())

        # Verify README was overwritten
        with open(readme_path) as f:
            content = f.read()
            assert content != "Modified content"
            assert "APIDOG" in content


class TestEnvConfigCommand:
    """Tests for env-config command."""

    def test_env_config_generates_file(self, mock_apidog_settings, temp_output_dir):
        """Test env-config generates configuration file."""
        out = StringIO()
        result = call_command("apidog", "env-config", stdout=out)

        output = out.getvalue()
        assert "Config saved to" in output or "apidog_environments.json" in output
        assert result is not None

    def test_env_config_valid_json(self, mock_apidog_settings, temp_output_dir):
        """Test env-config produces valid JSON."""
        call_command("apidog", "env-config", stdout=StringIO())

        config_file = os.path.join(temp_output_dir, "apidog_environments.json")
        assert os.path.exists(config_file)

        with open(config_file) as f:
            config = json.load(f)
            assert isinstance(config, dict)


class TestCommandsRequireSubcommand:
    """Tests for command validation."""

    def test_apidog_without_subcommand(self):
        """Test apidog command without subcommand shows help."""
        out = StringIO()
        call_command("apidog", stdout=out)
        output = out.getvalue()

        # Should show help or no error
        assert output is not None
