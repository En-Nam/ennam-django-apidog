# Testing Guide for ennam-django-apidog

## Overview

This document provides a comprehensive guide to testing the ennam-django-apidog library.

## Quick Start

```bash
# Install dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html
```

## Test Structure

### Test Files

| File | Tests | Purpose |
|------|-------|---------|
| `test_commands.py` | 13 | Core management commands (export, validate, init, env-config) |
| `test_commands_http.py` | 14 | HTTP API interactions with APIDOG (push, pull, compare) |
| `test_commands_errors.py` | 17 | Edge cases and error handling |
| `test_settings.py` | 7 | Settings configuration and credential handling |
| `test_schema_hooks.py` | 4 | drf-spectacular extension hooks |

**Total: 55 tests**

### Test Coverage

Current coverage: **40-50%** focusing on critical paths:

- ✅ HTTP API interactions (push/pull/compare with mocked responses)
- ✅ Management commands (export/validate/init)
- ✅ Settings and credential handling
- ✅ Error handling and edge cases
- ✅ Schema hooks for BaseSerializer subclasses

## Running Tests

### All Tests

```bash
pytest
```

### With Coverage Report

```bash
# Terminal output
pytest --cov=src --cov-report=term

# HTML report
pytest --cov=src --cov-report=html
# Open htmlcov/index.html in browser
```

### Specific Test File

```bash
pytest tests/test_commands_http.py -v
```

### Specific Test Class

```bash
pytest tests/test_commands.py::TestApidogCommand -v
```

### Specific Test

```bash
pytest tests/test_commands.py::TestApidogCommand::test_export_command -v
```

### With Markers

```bash
pytest -m integration    # Integration tests only
pytest -m smoke         # Smoke tests only
pytest -m regression    # Regression tests only
```

## HTTP Mocking

The library uses the `responses` library for HTTP mocking. This means:

- ✅ All APIDOG API calls are mocked
- ✅ No real API credentials needed for tests
- ✅ Fast test execution (no network calls)
- ✅ Deterministic test results

### Example Mocked Test

```python
@responses.activate
def test_push_success(self, mock_apidog_settings, temp_output_dir):
    """Test successful push to APIDOG."""
    # Export schema first
    call_command("apidog", "export", stdout=StringIO())

    # Mock APIDOG API response
    responses.add(
        responses.POST,
        "https://api.apidog.com/v1/projects/test-project-id/import-openapi",
        json={"success": True},
        status=200,
    )

    # Execute push command
    out = StringIO()
    call_command("apidog", "push", stdout=out)

    # Verify
    assert "Successfully pushed to APIDOG" in out.getvalue()
```

## Test Categories

### 1. HTTP Mocking Tests (test_commands_http.py)

Tests APIDOG API interactions with mocked responses:

- **TestPushCommand** (4 tests)
  - Success scenario
  - Custom file pushing
  - Authentication failures (401)
  - Missing credentials

- **TestPullCommand** (6 tests)
  - Success scenario
  - Custom output path
  - Authorization errors (401)
  - Project not found (404)
  - Server errors (500)
  - Missing credentials

- **TestCompareCommand** (4 tests)
  - Identical schemas (in sync)
  - Different schemas
  - Missing credentials
  - Auto-export local schema

### 2. Edge Case Tests (test_commands_errors.py)

Tests edge cases and error handling:

- **TestExportEdgeCases** (5 tests)
  - Directory creation
  - Custom filenames
  - YAML format
  - Latest version file
  - Custom indentation

- **TestValidateEdgeCases** (5 tests)
  - Invalid JSON handling
  - Missing required fields
  - Missing 'openapi' field
  - Nonexistent file handling
  - Default latest schema usage

- **TestInitEdgeCases** (4 tests)
  - Directory creation
  - Existing gitignore append
  - README generation
  - Force overwrite

### 3. Settings Tests (test_settings.py)

Tests configuration and credential handling:

- Default settings loading
- User settings override
- Environment variable override
- Credential retrieval with overrides
- Output directory calculation
- Invalid setting errors
- Cache clearing on reload

### 4. Schema Hooks Tests (test_schema_hooks.py)

Tests drf-spectacular extensions:

- BaseSerializerExtension class
- Schema mapping for BaseSerializer
- Preprocessing hooks

## Fixtures

### temp_output_dir

Creates a temporary directory for test files:

```python
def test_something(temp_output_dir):
    # temp_output_dir is a valid directory path
    pass
```

### mock_apidog_settings

Mocks APIDOG settings with test values:

```python
def test_something(mock_apidog_settings):
    # mock_apidog_settings['PROJECT_ID'] == 'test-project-id'
    # mock_apidog_settings['TOKEN'] == 'test-token'
    pass
```

## Code Quality Checks

### Type Checking

```bash
mypy src/
```

Expected: **Success: no issues found**

### Linting

```bash
ruff check src/ tests/
```

Expected: **All checks passed!**

### Code Formatting

```bash
ruff format src/ tests/
```

### Pre-commit Hooks

```bash
pre-commit install
pre-commit run --all-files
```

## Continuous Integration

Tests run automatically on GitHub Actions for:

- **Python**: 3.8, 3.9, 3.10, 3.11, 3.12
- **Django**: 3.2, 4.0, 4.1, 4.2, 5.0

See `.github/workflows/test.yml` for details.

## Development Workflow

1. **Write test first** (TDD approach)
2. **Run test to verify it fails**
3. **Implement feature**
4. **Run test to verify it passes**
5. **Run full test suite**
6. **Run pre-commit checks**
7. **Commit changes**

## Debugging Tests

### Verbose Output

```bash
pytest -v
pytest -vv  # Extra verbose
```

### Show Print Statements

```bash
pytest -s
```

### Stop on First Failure

```bash
pytest -x
```

### Failfast with Verbose

```bash
pytest -xvs
```

### Specific Log Level

```bash
pytest --log-level=DEBUG
```

## Known Issues

### pytest-django Compatibility

The library uses `pytest-django>=4.5.2` for Django integration. If you encounter:

```
AttributeError: module 'django.core.mail' has no attribute 'outbox'
```

Ensure you have the correct version:

```bash
pip install "pytest-django==4.5.2"
pip install "Django>=4.2,<5.0"
```

## Integration Testing with Real APIDOG

While unit tests use HTTP mocking, you can test with the real APIDOG API:

```python
# Set credentials
export APIDOG_PROJECT_ID="your-project-id"
export APIDOG_TOKEN="your-api-token"

# Use the package commands
python manage.py apidog export
python manage.py apidog push
python manage.py apidog pull
python manage.py apidog compare
```

## Contributing Tests

When contributing, ensure:

1. ✅ New tests follow existing patterns
2. ✅ All tests pass locally
3. ✅ Coverage doesn't decrease
4. ✅ Type hints are complete
5. ✅ Code passes ruff linting
6. ✅ Pre-commit hooks pass

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [responses library](https://github.com/getsentry/responses)
- [pytest-django](https://pytest-django.readthedocs.io/)
- [APIDOG API Reference](https://docs.apidog.com/)

## Support

For issues or questions about testing:

1. Check this documentation
2. Review test examples in `tests/`
3. Run with verbose flags (`-vv -s`)
4. Check CI logs on GitHub Actions
