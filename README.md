# ennam-django-apidog

[![PyPI version](https://badge.fury.io/py/ennam-django-apidog.svg)](https://badge.fury.io/py/ennam-django-apidog)
[![Python versions](https://img.shields.io/pypi/pyversions/ennam-django-apidog.svg)](https://pypi.org/project/ennam-django-apidog/)
[![Django versions](https://img.shields.io/badge/Django-3.2%20%7C%204.0%20%7C%204.1%20%7C%204.2%20%7C%205.0-green.svg)](https://www.djangoproject.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Django integration for [APIDOG](https://apidog.com) - Export, sync, and manage OpenAPI schemas between Django REST Framework and APIDOG Cloud.

## Features

- **Export OpenAPI Schema** - Generate OpenAPI 3.0 schemas from your Django REST Framework APIs
- **Sync with APIDOG Cloud** - Push and pull schemas to/from APIDOG Cloud
- **Compare Schemas** - Compare local schemas with cloud versions
- **Environment Management** - Generate environment configurations for different deployments
- **Schema Hooks** - Custom drf-spectacular extensions for handling edge cases
- **Templates** - Ready-to-use Makefile, Docker Compose, and configuration files

## Installation

```bash
pip install ennam-django-apidog
```

## Quick Start

### 1. Add to INSTALLED_APPS

```python
# settings.py
INSTALLED_APPS = [
    ...
    'rest_framework',
    'drf_spectacular',
    'ennam_django_apidog',
]
```

### 2. Configure DRF Spectacular

```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Your API',
    'DESCRIPTION': 'Your API description',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}
```

### 3. Add URL Routes

```python
# urls.py
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    ...
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
```

### 4. Initialize APIDOG

```bash
python manage.py apidog init
```

### 5. Export Schema

```bash
python manage.py apidog export
```

## Configuration

Configure APIDOG settings in your Django `settings.py`:

```python
APIDOG_SETTINGS = {
    # Output directory for schemas (default: apidog/ at project root)
    'OUTPUT_DIR': None,

    # Schema endpoint (default: /api/schema/)
    'SCHEMA_ENDPOINT': '/api/schema/',

    # APIDOG Cloud credentials
    'PROJECT_ID': 'your-project-id',  # or use env var APIDOG_PROJECT_ID
    'TOKEN': 'your-api-token',        # or use env var APIDOG_TOKEN

    # API configuration
    'API_VERSION': '2024-03-28',
    'API_BASE_URL': 'https://api.apidog.com/v1',
    'TIMEOUT': 60,

    # Environment configurations
    'ENVIRONMENTS': {
        'local': {
            'name': 'Local Development',
            'base_url': 'http://localhost:8000',
        },
        'production': {
            'name': 'Production',
            'base_url': 'https://api.yourapp.com',
        },
    },
}
```

Or use environment variables:

```bash
export APIDOG_PROJECT_ID="your-project-id"
export APIDOG_TOKEN="your-api-token"
```

## Commands

### Initialize Project

```bash
# Create apidog directory and templates
python manage.py apidog init

# Force overwrite existing files
python manage.py apidog init --force
```

### Export Schema

```bash
# Export as JSON (default)
python manage.py apidog export

# Export as YAML
python manage.py apidog export --format yaml

# Custom output directory
python manage.py apidog export --output /path/to/output/
```

### Validate Schema

```bash
# Validate latest schema
python manage.py apidog validate

# Validate specific file
python manage.py apidog validate --file /path/to/schema.json
```

### Push to APIDOG Cloud

```bash
# Push latest schema
python manage.py apidog push

# Push specific file
python manage.py apidog push --file /path/to/schema.json
```

### Pull from APIDOG Cloud

```bash
# Pull to default location
python manage.py apidog pull

# Pull to specific file
python manage.py apidog pull --output /path/to/output.json
```

### Compare Schemas

```bash
# Compare local with cloud
python manage.py apidog compare
```

### Generate Environment Config

```bash
python manage.py apidog env-config
```

## Using Schema Hooks

Add custom schema hooks to handle edge cases:

```python
# settings.py
SPECTACULAR_SETTINGS = {
    ...
    'PREPROCESSING_HOOKS': [
        'ennam_django_apidog.schema_hooks.preprocess_exclude_problematic_views',
    ],
    'EXTENSIONS': [
        'ennam_django_apidog.schema_hooks.BaseSerializerExtension',
    ],
}
```

## Makefile Commands

After running `apidog init`, use the Makefile for shortcuts:

```bash
# Show help
make -f Makefile.apidog help

# Export schema
make -f Makefile.apidog export

# Push to cloud
make -f Makefile.apidog push

# Compare with cloud
make -f Makefile.apidog compare

# Export and push
make -f Makefile.apidog sync
```

## Docker Support

Use the generated Docker Compose file for mock server:

```bash
# Start mock server
docker-compose -f docker-compose.apidog.yml up -d apidog-mock

# Mock server available at http://localhost:4010
```

## CI/CD Integration

Example GitHub Actions workflow:

```yaml
- name: Export OpenAPI Schema
  run: |
    python manage.py apidog export --format json

- name: Push to APIDOG
  env:
    APIDOG_PROJECT_ID: ${{ secrets.APIDOG_PROJECT_ID }}
    APIDOG_TOKEN: ${{ secrets.APIDOG_TOKEN }}
  run: |
    python manage.py apidog push
```

## Documentation

For full documentation, see [docs/GUIDE.md](docs/GUIDE.md).

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=html --cov-report=term

# Run specific test file
pytest tests/test_commands.py -v

# Run specific test
pytest tests/test_commands.py::TestApidogCommand::test_export_command -v

# Run tests with markers
pytest -m integration    # Integration tests only
```

### Test Coverage

Current coverage: **40-50%** focusing on critical functionality:
- ✅ HTTP API interactions (push/pull/compare with mocked responses)
- ✅ Management commands (export/validate/init)
- ✅ Settings and credential handling
- ✅ Error handling and edge cases

### Development Setup

```bash
# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run linting
ruff check src/ tests/
ruff format src/ tests/

# Run type checking
mypy src/

# Run all pre-commit checks
pre-commit run --all-files
```

### Pre-commit Hooks

This project uses pre-commit hooks for quality assurance:
- **ruff**: Code linting and formatting
- **mypy**: Static type checking with Django stubs
- **Standard checks**: YAML/TOML validation, trailing whitespace, etc.

Hooks run automatically on `git commit`. The same checks run in CI.

### Release Checklist

Before publishing to PyPI:

- [ ] All tests pass: `pytest --cov=src`
- [ ] Coverage ≥ 40%: `pytest --cov=src --cov-report=term`
- [ ] No mypy errors: `mypy src/`
- [ ] Linting passes: `ruff check src/ tests/`
- [ ] Pre-commit passes: `pre-commit run --all-files`
- [ ] CI passes on all Python/Django versions
- [ ] Version bumped in `pyproject.toml`
- [ ] CHANGELOG.md updated
- [ ] Test build: `python -m build && twine check dist/*`

### Continuous Integration

Tests run on GitHub Actions with:
- **Python versions**: 3.8, 3.9, 3.10, 3.11, 3.12
- **Django versions**: 3.2, 4.0, 4.1, 4.2, 5.0

See [.github/workflows/test.yml](.github/workflows/test.yml) for details.

## Requirements

- Python >= 3.8
- Django >= 3.2
- Django REST Framework >= 3.12
- drf-spectacular >= 0.26

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Links

- [APIDOG Website](https://apidog.com)
- [drf-spectacular Documentation](https://drf-spectacular.readthedocs.io/)
- [Django REST Framework](https://www.django-rest-framework.org/)
