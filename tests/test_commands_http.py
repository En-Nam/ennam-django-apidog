"""Tests for APIDOG API HTTP interactions using responses library."""
import json
from io import StringIO

import pytest
import responses
from django.core.management import call_command
from django.core.management.base import CommandError


class TestPushCommand:
    """Tests for push command with HTTP mocking."""

    @responses.activate
    def test_push_success(self, mock_apidog_settings, temp_output_dir):
        """Test successful push to APIDOG Cloud."""
        # Export schema first
        call_command("apidog", "export", stdout=StringIO())

        # Mock APIDOG API
        responses.add(
            responses.POST,
            "https://api.apidog.com/v1/projects/test-project-id/import-openapi",
            json={"success": True},
            status=200,
        )

        # Execute push
        out = StringIO()
        call_command("apidog", "push", stdout=out)
        output = out.getvalue()

        # Verify
        assert "Successfully pushed to APIDOG" in output
        assert len(responses.calls) == 1

    @responses.activate
    def test_push_with_custom_file(self, mock_apidog_settings, temp_output_dir):
        """Test push with custom file specified."""
        import os

        # Create a custom schema file
        custom_file = os.path.join(temp_output_dir, "custom_schema.json")
        schema = {
            "openapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {},
        }
        with open(custom_file, "w") as f:
            json.dump(schema, f)

        # Mock APIDOG API
        responses.add(
            responses.POST,
            "https://api.apidog.com/v1/projects/test-project-id/import-openapi",
            json={"success": True},
            status=200,
        )

        # Execute push with custom file
        out = StringIO()
        call_command("apidog", "push", file=custom_file, stdout=out)

        assert "Successfully pushed to APIDOG" in out.getvalue()

    @responses.activate
    def test_push_authentication_failure(self, mock_apidog_settings, temp_output_dir):
        """Test push with 401 authentication error."""
        call_command("apidog", "export", stdout=StringIO())

        responses.add(
            responses.POST,
            "https://api.apidog.com/v1/projects/test-project-id/import-openapi",
            status=401,
        )

        out = StringIO()
        call_command("apidog", "push", stdout=out)
        output = out.getvalue()

        # Should show failure
        assert "Failed" in output or "401" in output

    @responses.activate
    def test_push_without_credentials(self, temp_output_dir):
        """Test push fails gracefully without credentials."""
        call_command("apidog", "export", stdout=StringIO())

        # Don't mock - test should fail before API call
        with pytest.raises(CommandError) as exc_info:
            call_command("apidog", "push", stdout=StringIO())

        assert "credentials required" in str(exc_info.value).lower()


class TestPullCommand:
    """Tests for pull command with HTTP mocking."""

    @responses.activate
    def test_pull_success(self, mock_apidog_settings, temp_output_dir):
        """Test successful pull from APIDOG Cloud."""
        mock_schema = {
            "openapi": "3.0.0",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {"/test/": {"get": {}}},
        }

        responses.add(
            responses.POST,
            "https://api.apidog.com/v1/projects/test-project-id/export-openapi",
            json=mock_schema,
            status=200,
        )

        out = StringIO()
        result = call_command("apidog", "pull", stdout=out)
        output = out.getvalue()

        assert "Schema pulled to:" in output
        assert result is not None

    @responses.activate
    def test_pull_with_custom_output(self, mock_apidog_settings, temp_output_dir):
        """Test pull with custom output file."""
        import os

        mock_schema = {
            "openapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {},
        }

        custom_output = os.path.join(temp_output_dir, "custom_pull.json")

        responses.add(
            responses.POST,
            "https://api.apidog.com/v1/projects/test-project-id/export-openapi",
            json=mock_schema,
            status=200,
        )

        call_command("apidog", "pull", output=custom_output, stdout=StringIO())

        assert os.path.exists(custom_output)

    @responses.activate
    def test_pull_unauthorized(self, mock_apidog_settings, temp_output_dir):
        """Test pull with 401 authorization error."""
        responses.add(
            responses.POST,
            "https://api.apidog.com/v1/projects/test-project-id/export-openapi",
            status=401,
        )

        with pytest.raises(CommandError) as exc_info:
            call_command("apidog", "pull", stdout=StringIO())

        assert "Unauthorized" in str(exc_info.value)

    @responses.activate
    def test_pull_project_not_found(self, mock_apidog_settings, temp_output_dir):
        """Test pull with 404 project not found error."""
        responses.add(
            responses.POST,
            "https://api.apidog.com/v1/projects/test-project-id/export-openapi",
            status=404,
        )

        with pytest.raises(CommandError) as exc_info:
            call_command("apidog", "pull", stdout=StringIO())

        assert "not found" in str(exc_info.value).lower()

    @responses.activate
    def test_pull_server_error(self, mock_apidog_settings, temp_output_dir):
        """Test pull with server error."""
        responses.add(
            responses.POST,
            "https://api.apidog.com/v1/projects/test-project-id/export-openapi",
            status=500,
        )

        with pytest.raises(CommandError):
            call_command("apidog", "pull", stdout=StringIO())

    @responses.activate
    def test_pull_without_credentials(self, temp_output_dir):
        """Test pull fails without credentials."""
        with pytest.raises(CommandError) as exc_info:
            call_command("apidog", "pull", stdout=StringIO())

        assert "credentials required" in str(exc_info.value).lower()


class TestCompareCommand:
    """Tests for compare command with HTTP mocking."""

    @responses.activate
    def test_compare_schemas_sync(self, mock_apidog_settings, temp_output_dir):
        """Test compare when schemas are identical."""
        # Export local schema
        call_command("apidog", "export", stdout=StringIO())

        # Mock identical schema from cloud
        mock_schema = {
            "openapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {},
        }

        responses.add(
            responses.POST,
            "https://api.apidog.com/v1/projects/test-project-id/export-openapi",
            json=mock_schema,
            status=200,
        )

        out = StringIO()
        result = call_command("apidog", "compare", stdout=out)
        output = out.getvalue()

        assert "COMPARISON" in output or "endpoints" in output.lower()
        assert result is not None

    @responses.activate
    def test_compare_schemas_different(self, mock_apidog_settings, temp_output_dir):
        """Test compare when schemas have different endpoints."""
        call_command("apidog", "export", stdout=StringIO())

        # Mock different schema
        mock_schema = {
            "openapi": "3.0.0",
            "info": {"title": "Different", "version": "2.0.0"},
            "paths": {"/different/": {"post": {}}},
        }

        responses.add(
            responses.POST,
            "https://api.apidog.com/v1/projects/test-project-id/export-openapi",
            json=mock_schema,
            status=200,
        )

        out = StringIO()
        result = call_command("apidog", "compare", stdout=out)

        assert result is not None
        assert isinstance(result, dict)
        assert "local_only" in result or "cloud_only" in result or "common" in result

    @responses.activate
    def test_compare_without_credentials(self, temp_output_dir):
        """Test compare fails without credentials."""
        with pytest.raises(CommandError) as exc_info:
            call_command("apidog", "compare", stdout=StringIO())

        assert "credentials required" in str(exc_info.value).lower()

    @responses.activate
    def test_compare_auto_exports_local(self, mock_apidog_settings, temp_output_dir):
        """Test compare auto-exports local schema if missing."""
        mock_schema = {
            "openapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {},
        }

        # Mock both export and pull
        responses.add(
            responses.POST,
            "https://api.apidog.com/v1/projects/test-project-id/export-openapi",
            json=mock_schema,
            status=200,
        )

        out = StringIO()
        result = call_command("apidog", "compare", stdout=out)

        assert result is not None
