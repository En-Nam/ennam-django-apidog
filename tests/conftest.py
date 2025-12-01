"""Pytest configuration and fixtures."""

import os
import shutil
import tempfile

import django
import pytest
from django.conf import settings


@pytest.fixture(scope="session", autouse=True)
def setup_django() -> None:
    """Setup Django for testing."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.settings")
    if not settings.configured:
        django.setup()


def pytest_configure(config: object) -> None:
    """Configure pytest without triggering django fixtures for non-django tests."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.settings")


@pytest.fixture
def temp_output_dir() -> str:
    """Create a temporary output directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_apidog_settings(temp_output_dir: str, monkeypatch: pytest.MonkeyPatch) -> dict:
    """Mock APIDOG settings for testing."""
    test_settings = {
        "OUTPUT_DIR": temp_output_dir,
        "SCHEMA_ENDPOINT": "/api/schema/",
        "PROJECT_ID": "test-project-id",
        "TOKEN": "test-token",
        "ENVIRONMENTS": {
            "local": {
                "name": "Local Development",
                "base_url": "http://localhost:8000",
            },
        },
    }
    monkeypatch.setattr(settings, "APIDOG_SETTINGS", test_settings)

    # Reload settings
    from ennam_django_apidog.settings import apidog_settings
    apidog_settings.reload()

    yield test_settings

    # Cleanup
    apidog_settings.reload()
