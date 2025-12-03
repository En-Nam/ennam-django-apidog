# ennam-django-apidog

Django integration for APIDOG - Export, sync, and manage OpenAPI schemas between Django REST Framework and APIDOG Cloud.

## Features

- **Export OpenAPI Schema**: Generate OpenAPI 3.0.3 schemas from Django REST Framework
- **Push to APIDOG Cloud**: Upload schemas to APIDOG project
- **Pull from APIDOG Cloud**: Download schemas from APIDOG project
- **Schema Validation**: Validate OpenAPI schema files
- **Schema Comparison**: Compare local and cloud schemas
- **Environment Configuration**: Generate APIDOG environment configurations

## Installation

```bash
pip install ennam-django-apidog
```

## Quick Start

### 1. Add to Django Settings

```python
INSTALLED_APPS = [
    'rest_framework',
    'drf_spectacular',
    'ennam_django_apidog',
]

APIDOG_SETTINGS = {
    'PROJECT_ID': '1133189',
    'TOKEN': 'your-apidog-token',
    'OUTPUT_DIR': 'apidog',
}
```

### 2. Available Commands

```bash
# Initialize APIDOG directory structure
python manage.py apidog init

# Export OpenAPI schema from Django
python manage.py apidog export

# Validate OpenAPI schema
python manage.py apidog validate

# Push schema to APIDOG Cloud
python manage.py apidog push

# Pull schema from APIDOG Cloud
python manage.py apidog pull

# Compare local and cloud schemas
python manage.py apidog compare

# Generate environment configuration
python manage.py apidog env-config
```

## Configuration

### Using Environment Variables

Instead of hardcoding credentials in settings, use environment variables:

```python
import os

APIDOG_SETTINGS = {
    'PROJECT_ID': os.getenv('APIDOG_PROJECT_ID'),
    'TOKEN': os.getenv('APIDOG_TOKEN'),
    'OUTPUT_DIR': os.path.join(BASE_DIR, 'apidog'),
}
```

Then set environment variables:
```bash
export APIDOG_PROJECT_ID=1133189
export APIDOG_TOKEN=your-token
```

## Development

### Install Development Dependencies

```bash
pip install -e ".[dev]"
```

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_commands.py
```

### Code Quality

```bash
# Type checking
mypy src/

# Linting
ruff check src/

# Format code
ruff check src/ --fix
```

## Build & Publish

### Build Distribution Packages

```bash
python -m build
```

This creates:
- `dist/ennam_django_apidog-X.Y.Z.tar.gz`
- `dist/ennam_django_apidog-X.Y.Z-py3-none-any.whl`

### Verify Packages

```bash
python -m twine check dist/*
```

### Publish to PyPI (Manual)

**Option 1: Web Upload**
1. Go to https://pypi.org/legacy/
2. Login with your PyPI account
3. Click "Upload file"
4. Select both `.tar.gz` and `.whl` files

**Option 2: Command Line with Token**

Create `~/.pypirc`:
```ini
[distutils]
index-servers = pypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-AgEIcHlwaS5vcmcCJ...
```

Then upload:
```bash
python -m twine upload dist/*
```

## Project Structure

```
ennam-django-apidog/
├── src/ennam_django_apidog/
│   ├── management/commands/apidog.py    # Main command (660 lines)
│   ├── settings.py                       # Settings management
│   ├── schema_hooks.py                   # drf-spectacular hooks
│   └── templates/                        # Template files
├── tests/                                # Test suite
├── pyproject.toml                        # Project configuration
└── README.md                             # This file
```

## APIDOG API Integration

The package uses APIDOG's REST API:

- **Authentication**: Bearer token
- **Base URL**: `https://api.apidog.com/v1`
- **Push Endpoint**: `POST /projects/{id}/import-openapi`
- **Pull Endpoint**: `POST /projects/{id}/export-openapi`

## Requirements

- Django >= 3.2
- Django REST Framework >= 3.12
- drf-spectacular >= 0.26
- requests
- PyYAML

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or contributions, please contact:
- Email: danny.tranhoang@ennam.vn
- Package: https://pypi.org/project/ennam-django-apidog/
