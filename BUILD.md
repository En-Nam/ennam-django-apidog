# Build & Publish Setup for ennam-django-apidog

Complete guide to the build and publishing infrastructure for ennam-django-apidog.

## Overview

The project is fully configured for:
- ✅ Continuous testing with pytest
- ✅ Type safety with mypy (strict mode)
- ✅ Code quality with ruff
- ✅ Pre-commit hooks for automated checks
- ✅ Automated distribution building
- ✅ PyPI publishing via GitHub Actions
- ✅ TestPyPI testing before production release

## Quick Commands

### Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Type checking
mypy src/ --strict

# Linting
ruff check src/ tests/

# Code formatting
ruff format src/ tests/

# Pre-commit checks
pre-commit install
pre-commit run --all-files
```

### Building

```bash
# Build wheel and source distributions
python -m build

# Verify distributions
python -m twine check dist/*

# Clean build artifacts
rm -rf build/ dist/ *.egg-info/
```

### Publishing

**Method 1: GitHub Release (Recommended)**
1. Create release on GitHub
2. Tag: `vX.Y.Z`
3. Workflow automatically publishes to PyPI

**Method 2: Manual Workflow**
1. Go to GitHub Actions
2. Run "Publish to PyPI" workflow
3. Choose environment (testpypi or pypi)

## Project Files

### Configuration Files

| File | Purpose |
|------|---------|
| `pyproject.toml` | Project metadata, dependencies, tool configuration |
| `.pre-commit-config.yaml` | Pre-commit hooks configuration |
| `pytest.ini` | Pytest configuration |
| `.gitignore` | Git exclusion patterns |

### Workflow Files

| File | Purpose |
|------|---------|
| `.github/workflows/test.yml` | Automated testing on push/PR |
| `.github/workflows/publish.yml` | Automated PyPI publishing |

### Documentation

| File | Purpose |
|------|---------|
| `README.md` | Project overview and usage |
| `TESTING.md` | Complete testing guide |
| `RELEASE.md` | Release process checklist |
| `PUBLISH.md` | Publishing quick reference |
| `CLAUDE.md` | Architecture and development notes |
| `BUILD.md` | This file - build infrastructure overview |

### Source Code

```
src/ennam_django_apidog/
├── __init__.py              # Package initialization
├── apps.py                  # Django app config
├── settings.py              # Configuration management
├── schema_hooks.py          # DRF-spectacular extensions
├── py.typed                 # PEP 561 marker
└── management/commands/
    └── apidog.py            # Main CLI command
```

### Tests

```
tests/
├── conftest.py              # Pytest configuration and fixtures
├── settings.py              # Django test settings
├── test_commands.py         # Management command tests
├── test_commands_http.py    # HTTP API mocking tests
├── test_commands_errors.py  # Edge case tests
├── test_settings.py         # Configuration tests
└── test_schema_hooks.py     # Schema extension tests
```

## Testing Pipeline

### Local Testing

```bash
# All tests with coverage
pytest --cov=src --cov-report=html

# Specific test file
pytest tests/test_commands_http.py -v

# Specific test
pytest tests/test_commands_http.py::TestPushCommand::test_push_success -v

# Run with markers
pytest -m integration
```

### CI/CD Testing (GitHub Actions)

Runs automatically on:
- **Push to main/develop**: Full test suite
- **Pull requests**: Full test suite
- **Test matrix**: Python 3.8-3.12 × Django 3.2-5.0

**Test Steps:**
1. Run ruff linting
2. Run pytest with coverage
3. Run strict mypy type checking
4. Upload coverage to codecov (Python 3.10 + Django 4.2 only)

## Build Pipeline

### Local Building

```bash
# Create distributions
python -m build

# Result files:
# dist/ennam_django_apidog-0.1.0.tar.gz     # Source distribution
# dist/ennam_django_apidog-0.1.0-py3-none-any.whl  # Wheel

# Verify with twine
python -m twine check dist/*
```

### CI/CD Building (GitHub Actions - publish.yml)

Runs when:
- GitHub Release is created
- Manual workflow dispatch

**Build Steps:**
1. **Build Job**
   - Create wheel and source distributions
   - Verify with twine
   - Upload artifacts

2. **Test Job**
   - Download artifacts
   - Install wheel
   - Verify import works

3. **Publish Jobs**
   - TestPyPI (always)
   - PyPI (if not pre-release)

4. **Verify Job**
   - Test installation from PyPI
   - Confirm package available

## Publishing Pipeline

### Automated Publishing

**Trigger 1: GitHub Release**
```
Create Release (GitHub)
    ↓
Trigger publish.yml workflow
    ↓
Build distributions
    ↓
Test build integrity
    ↓
Publish to TestPyPI
    ↓
Verify TestPyPI installation
    ↓
Publish to PyPI (if not pre-release)
    ↓
Verify PyPI installation
```

**Trigger 2: Manual Workflow Dispatch**
```
Actions → Publish to PyPI → Run workflow
    ↓
Choose environment (testpypi or pypi)
    ↓
Proceed with publish steps above
```

### Version Strategy

**Before Publishing**
1. Update version in `pyproject.toml`
2. Create git tag: `git tag -a vX.Y.Z -m "Release version X.Y.Z"`
3. Push tag: `git push origin vX.Y.Z`
4. Create GitHub Release from tag

**Version Numbers**
- Beta: `0.MINOR.PATCH` (e.g., 0.1.0, 0.2.0)
- Stable: `MAJOR.MINOR.PATCH` (e.g., 1.0.0, 1.1.0)

## Quality Gates

### Type Safety
```bash
mypy src/ --strict
```
- Source files: `disallow_untyped_defs = true`
- Test files: Type checking allowed to be less strict
- Uses type stubs for Django, DRF, requests, PyYAML

### Code Quality
```bash
ruff check src/ tests/
ruff format src/ tests/
```
- Linting: PEP 8 compliance
- Formatting: Consistent code style
- Security: Basic security checks

### Testing
```bash
pytest --cov=src --cov-report=html
```
- Coverage target: 40-50%
- Focus areas: Critical functionality, error handling
- HTTP mocking: Uses `responses` library

### Pre-commit Hooks
```bash
pre-commit install
pre-commit run --all-files
```
Auto-runs on commit:
- Trailing whitespace
- YAML validation
- TOML validation
- Merge conflict detection
- Ruff checking
- Mypy type checking

## Troubleshooting

### Tests Fail

```bash
# Reinstall dependencies
pip install -e ".[dev]"

# Run with verbose output
pytest -vv

# Run with print statements
pytest -s

# Stop on first failure
pytest -x
```

### Type Errors

```bash
# Check mypy output
mypy src/ --strict

# Fix with strict mode
# Review CLAUDE.md for type annotation patterns
```

### Build Fails

```bash
# Clean old builds
rm -rf build/ dist/ *.egg-info/

# Rebuild
python -m build

# Check with twine
python -m twine check dist/*
```

### PyPI Upload Fails

See [PUBLISH.md](PUBLISH.md) troubleshooting section.

## Files Modified for Build & Publish

### Configuration Updates
- `pyproject.toml`: Added dev dependencies and mypy config
- `.pre-commit-config.yaml`: Created with quality hooks
- `pytest.ini`: Markers and Django configuration
- `.gitignore`: Patterns for build artifacts

### Workflow Files
- `.github/workflows/test.yml`: Updated mypy configuration
- `.github/workflows/publish.yml`: Created with full publishing pipeline

### Source Code
- All files: Added strict type hints
- `src/ennam_django_apidog/py.typed`: Created for PEP 561

### Documentation
- `TESTING.md`: Comprehensive testing guide
- `RELEASE.md`: Release process checklist
- `PUBLISH.md`: Publishing quick reference
- `CLAUDE.md`: Architecture and development notes

## Security Considerations

### No Credentials in Code
- ✅ No API tokens
- ✅ No hardcoded secrets
- ✅ No credentials in git history

### Secure Publishing
- ✅ Uses PyPI Trusted Publishers (no token storage)
- ✅ GitHub Actions verification required
- ✅ Automatic credential management
- ✅ No manual twine uploads

### Pre-publish Verification
- ✅ All tests pass
- ✅ Type checking strict
- ✅ Linting passes
- ✅ Distributions verified with twine
- ✅ Installation tested

## Next Steps

1. **Test the workflow locally**
   ```bash
   pytest
   mypy src/ --strict
   python -m build
   ```

2. **Create a release**
   - Update version in `pyproject.toml`
   - Create git tag
   - Push to GitHub
   - Create GitHub Release

3. **Monitor publishing**
   - Watch GitHub Actions workflow
   - Check PyPI package page (5-10 min delay)
   - Install and verify

4. **Post-release**
   - Update version for next development cycle
   - Plan next features
   - Monitor issues/feedback

## Resources

- **PyPI Package**: https://pypi.org/project/ennam-django-apidog/
- **GitHub Repository**: https://github.com/ennam/ennam-django-apidog
- **Test PyPI**: https://test.pypi.org/project/ennam-django-apidog/

## Related Documentation

- [TESTING.md](TESTING.md) - Complete testing guide
- [RELEASE.md](RELEASE.md) - Release process checklist
- [PUBLISH.md](PUBLISH.md) - Publishing quick reference
- [CLAUDE.md](CLAUDE.md) - Architecture and development notes
- [README.md](README.md) - Project overview

## Support

For build and publish issues:

1. Check GitHub Actions logs
2. Review relevant documentation above
3. Check the troubleshooting section
4. Review Python packaging documentation
5. Contact maintainers if needed
