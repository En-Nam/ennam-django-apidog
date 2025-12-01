# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**ennam-django-apidog** is a Django package that integrates with APIDOG for OpenAPI schema management. It provides Django management commands to export, validate, push, pull, and compare OpenAPI schemas between Django REST Framework applications and APIDOG Cloud.

**Key Dependencies:**
- Django >= 3.2
- djangorestframework >= 3.12
- drf-spectacular >= 0.26 (handles OpenAPI schema generation)
- requests, PyYAML

## Architecture

### Core Components

1. **Management Command** (`src/ennam_django_apidog/management/commands/apidog.py`)
   - Main entry point: `python manage.py apidog <subcommand>`
   - Subcommands: `init`, `export`, `validate`, `push`, `pull`, `compare`, `env-config`
   - Uses Django's test Client to fetch schemas from drf-spectacular endpoints
   - Makes HTTP requests to APIDOG Cloud API for push/pull/compare operations

2. **Settings Module** (`src/ennam_django_apidog/settings.py`)
   - `ApidogSettings` class provides configuration management
   - Settings hierarchy: Django `APIDOG_SETTINGS` dict → environment variables → defaults
   - Key methods: `get_output_dir()`, `get_credentials()`, `reload()`
   - Supports per-environment configuration (local, dev, staging, production)

3. **Schema Hooks** (`src/ennam_django_apidog/schema_hooks.py`)
   - `BaseSerializerExtension`: drf-spectacular extension for handling BaseSerializer subclasses
   - `preprocess_exclude_problematic_views()`: Hook to filter problematic endpoints
   - These are registered in Django's `SPECTACULAR_SETTINGS`

4. **Templates** (`src/ennam_django_apidog/templates/`)
   - Generated during `apidog init`: Makefile, docker-compose, environment configs, .gitignore

### Data Flow

1. **Export**: Django Client → drf-spectacular endpoint → JSON/YAML schema file
2. **Push**: Local schema file → HTTP POST to APIDOG `/import-openapi` endpoint
3. **Pull**: HTTP POST to APIDOG `/export-openapi` endpoint → Local schema file
4. **Compare**: Export/fetch both local and cloud schemas → Compare endpoints → Report diff

### Configuration

Settings are read from (in priority order):
1. Django `APIDOG_SETTINGS` dict in settings.py
2. Environment variables: `APIDOG_PROJECT_ID`, `APIDOG_TOKEN`, `APIDOG_OUTPUT_DIR`
3. Command-line arguments: `--project-id`, `--token`
4. Defaults from `DEFAULTS` dict in settings.py

## Commands

### Development & Testing

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_commands.py

# Run tests with specific marker
pytest -m smoke
pytest -m regression

# Run single test
pytest tests/test_hello.py::test_hello

# Format code with ruff
ruff check src --fix

# Type checking
mypy src

# Build distribution
python -m build
```

### Building & Publishing

```bash
# Build package
python -m build

# Check built files
twine check dist/*

# Publish to PyPI (requires credentials)
twine upload dist/*
```

## Testing

- **Framework**: pytest with pytest-django
- **Configuration**: `pytest.ini` and `pyproject.toml [tool.pytest.ini_options]`
- **Django Setup**: Auto-configured via `conftest.py` fixture
- **Test Directory**: `tests/`
- **Test Modules**:
  - `test_commands.py`: Tests for management commands
  - `test_settings.py`: Tests for settings module
  - `test_schema_hooks.py`: Tests for drf-spectacular extensions
  - `test_hello.py`: Placeholder test
- **Fixtures**:
  - `temp_output_dir`: Creates temp directory for test files
  - `mock_apidog_settings`: Mocks APIDOG settings with test values

## Key Implementation Details

### Management Command Structure

The `apidog.py` command follows this pattern:

```python
class Command(BaseCommand):
    def add_arguments(self, parser):
        # Define subparsers for each subcommand

    def handle(self, *args, **options):
        # Route to appropriate handler based on subcommand

    def handle_<subcommand>(self, options):
        # Implement specific subcommand logic
```

### Schema Export

- Uses `Django test Client` to make internal requests to `SCHEMA_ENDPOINT`
- Fetches from drf-spectacular endpoint (default: `/api/schema/`)
- Adds metadata: `x-generated-at`, `x-generated-by`
- Saves both timestamped and "latest" versions
- Supports JSON and YAML formats

### APIDOG API Integration

- **Base URL**: `https://api.apidog.com/v1` (configurable)
- **Authentication**: Bearer token in Authorization header
- **Endpoints**:
  - POST `/projects/{id}/import-openapi`: Push schemas
  - POST `/projects/{id}/export-openapi`: Pull schemas
- **API Version Header**: `X-Apidog-Api-Version` (default: 2024-03-28)
- **Timeout**: Configurable (default: 60 seconds)

### Output Directory Structure

After `apidog init`:
```
project_root/
├── apidog/
│   ├── README.md
│   ├── environments.json
│   ├── openapi_schema_latest.json
│   ├── openapi_schema_YYYYMMDD_HHMMSS.json
│   └── openapi_from_apidog_YYYYMMDD_HHMMSS.json
├── Makefile.apidog
├── docker-compose.apidog.yml
└── .gitignore (updated with apidog rules)
```

## Common Development Tasks

### Adding a New Subcommand

1. Add argument parser in `add_arguments()` method
2. Add routing in `handle()` method for the new subcommand
3. Implement `handle_<subcommand>()` method in Command class
4. Add tests in `tests/test_commands.py`

### Modifying Settings Behavior

- Edit `DEFAULTS` dict in `settings.py` for new configuration options
- Add corresponding environment variable handling in `ApidogSettings.__getattr__()`
- Add methods to `ApidogSettings` for accessing/processing settings

### Extending Schema Hooks

- Subclass `OpenApiSerializerExtension` from drf-spectacular
- Implement `get_name()` and `map_serializer()` methods
- Register in Django's `SPECTACULAR_SETTINGS['EXTENSIONS']`

## Package Structure

```
src/ennam_django_apidog/
├── __init__.py               # Package exports
├── apps.py                   # Django AppConfig
├── settings.py               # Settings management
├── schema_hooks.py           # drf-spectacular extensions
├── management/
│   ├── __init__.py
│   └── commands/
│       ├── __init__.py
│       └── apidog.py         # Main command (700+ lines)
├── templates/                # Template files (copied during init)
│   ├── Makefile.apidog
│   ├── docker-compose.apidog.yml
│   ├── environments.json
│   └── .gitignore.apidog
└── py.typed                  # PEP 561 marker for type hints
```

## Notes for Future Development

- The `apidog.py` command is large (660 lines). If adding new subcommands, consider refactoring handlers into separate modules.
- APIDOG Cloud API requests use HTTP POST with JSON payloads; no official SDK is used.
- Schema comparison only compares endpoint paths, not detailed schema differences.
- The package expects drf-spectacular to be properly configured in the Django project.
- Error handling in cloud API calls provides HTTP status-specific messages (401, 404, etc.).
