# Publishing Guide for ennam-django-apidog

Quick reference guide for publishing the ennam-django-apidog package to PyPI.

## Quick Publish Checklist

Use this for a quick reference before publishing:

```bash
# 1. Verify everything is working
pytest                           # Run all tests
mypy src/ --strict              # Type checking
ruff check src/ tests/          # Linting

# 2. Build locally
python -m build                 # Create distributions
python -m twine check dist/*    # Verify distributions

# 3. Update version in pyproject.toml
# version = "0.2.0"

# 4. Create git tag and push
git tag -a v0.2.0 -m "Release version 0.2.0"
git push origin v0.2.0

# 5. Create GitHub Release - workflow handles publishing
```

## Two Publishing Methods

### Method 1: Automated via GitHub Release (Recommended)

1. **Navigate to GitHub repository**
2. **Click "Releases" → "Draft a new release"**
3. **Create release:**
   - Tag version: `vX.Y.Z` (e.g., `v0.2.0`)
   - Release title: `Release version X.Y.Z`
   - Add release notes with features/fixes
4. **Publish release**
   - Automatically triggers `publish.yml` workflow
   - Builds and publishes to TestPyPI
   - Publishes to production PyPI
   - Verification happens automatically

### Method 2: Manual Workflow Dispatch

If you need to publish without creating a release:

1. **Go to GitHub repo → Actions tab**
2. **Select "Publish to PyPI" workflow**
3. **Click "Run workflow"**
4. **Choose environment:**
   - `testpypi` - Test on TestPyPI first
   - `pypi` - Direct to PyPI (production)

## Pre-Publishing Requirements

Before any publish attempt:

### ✅ Code Quality

```bash
# All tests must pass
pytest -v

# Zero type errors
mypy src/ --strict

# No linting issues
ruff check src/ tests/
```

### ✅ Version Updated

```bash
# In pyproject.toml
[project]
version = "0.2.0"
```

### ✅ Git State

```bash
# Working directory clean
git status
# On main branch
git branch
# All changes committed
git log -1
```

## Publish Workflow Steps

### 1. Build Phase
- Downloads source code
- Installs build dependencies
- Creates wheel (.whl) and source (.tar.gz) distributions
- Verifies distributions with twine
- Uploads to GitHub artifacts

### 2. Test Phase
- Downloads artifacts
- Installs built wheel
- Imports package successfully
- Confirms installation works

### 3. TestPyPI Phase (if triggered)
- Publishes to https://test.pypi.org/
- Allows safe testing before production
- Full verification of PyPI metadata

### 4. PyPI Phase (for releases only)
- Publishes to https://pypi.org/
- Makes package available to `pip install`
- Automatic only if not a pre-release version

### 5. Verification Phase
- Waits for PyPI indexing (30 seconds)
- Tests installation from TestPyPI
- Tests installation from PyPI
- Confirms package availability

## Monitoring the Publish

### GitHub Actions Workflow

1. **Go to Actions tab**
2. **Find "Publish to PyPI" workflow run**
3. **Click to see detailed logs**

Each step shows:
- ✅ **Passed**: Step completed successfully
- ❌ **Failed**: Step encountered error
- ⏭️ **Skipped**: Step conditions not met

### Common Status Outcomes

| Status | Meaning |
|--------|---------|
| All green ✅ | Publish successful |
| TestPyPI only | Publishing to test environment |
| PyPI marked 'skip' | Pre-release, only TestPyPI |
| Build fails ❌ | Code issue, fix and retry |
| TestPyPI passes, PyPI fails ❌ | PyPI setup issue, check credentials |

## Post-Publish Verification

### 1. PyPI Package Page

```bash
# Visit package page (wait 5-10 minutes for indexing)
https://pypi.org/project/ennam-django-apidog/
```

### 2. TestPyPI Package Page

```bash
# For test releases
https://test.pypi.org/project/ennam-django-apidog/
```

### 3. Install and Test

```bash
# Create temporary environment
python -m venv temp_env
source temp_env/bin/activate  # On Windows: temp_env\Scripts\activate

# Install from PyPI
pip install ennam-django-apidog

# Verify installation
python -c "import ennam_django_apidog; print('Success!')"

# Check version
python -c "import ennam_django_apidog; print(ennam_django_apidog.__version__)"

# Test Django integration
python manage.py apidog export

# Cleanup
deactivate
rm -rf temp_env
```

## Version Numbers

### Beta Releases (0.x.y)

Format: `0.MINOR.PATCH`

- Pre-release versions
- API may change between releases
- Not for production use
- Example: `0.1.0`, `0.1.1`, `0.2.0`

**Publishing:**
- Only to TestPyPI and PyPI
- Both treated as normal releases

### Stable Releases (1.0.0+)

Format: `MAJOR.MINOR.PATCH`

- Production-ready
- Semantic versioning
- Breaking changes: bump MAJOR
- Features: bump MINOR
- Fixes: bump PATCH

**Examples:**
- `1.0.0` - Initial stable release
- `1.1.0` - New features (backward compatible)
- `1.1.1` - Bug fix (backward compatible)
- `2.0.0` - Major version with breaking changes

## Troubleshooting

### Build Fails

**Error**: `python -m build` fails with dependency errors

**Solution**:
```bash
# Clean previous builds
rm -rf build/ dist/ *.egg-info/

# Reinstall dependencies
pip install -e ".[dev]"

# Try again
python -m build
```

### TestPyPI Upload Succeeds, PyPI Fails

**Error**: Can upload to TestPyPI but PyPI upload fails

**Causes:**
1. PyPI credentials not configured
2. Version already exists on PyPI
3. Package metadata issues

**Solutions**:
```bash
# Check if version exists
curl https://pypi.org/pypi/ennam-django-apidog/0.2.0/json

# Use workflow dispatch for manual retry
# Go to Actions → Publish to PyPI → Run workflow → Choose 'pypi'
```

### Package Not Appearing on PyPI

**Issue**: Uploaded successfully but package not showing

**Solution**:
- Wait 5-10 minutes for PyPI indexing
- Clear pip cache: `pip cache purge`
- Try installing: `pip install --no-cache-dir ennam-django-apidog`

### GitHub Secrets Missing

**Error**: Workflow fails because PyPI credentials not configured

**Solution**:
1. Go to GitHub repo settings
2. Secrets and variables → Actions
3. Add required secrets (handled by PyPI trusted publisher)

## Security

### No Local Upload

Never run:
```bash
# ❌ Don't do this locally
twine upload dist/*
```

Always use GitHub Actions workflow for automated, audited publishing.

### Credentials

The workflow uses **PyPI Trusted Publishers**, which is more secure than API tokens:

- No tokens stored in GitHub
- Publishing verified via GitHub
- Automatic credential management
- Revokable at PyPI if needed

### Pre-Publish Checks

The workflow automatically:
- ✅ Verifies distributions with twine
- ✅ Tests installation
- ✅ Confirms no malicious content
- ✅ Validates package metadata

## FAQ

### Q: How do I publish without a GitHub release?

A: Use workflow dispatch:
1. Go to Actions tab
2. Select "Publish to PyPI"
3. Click "Run workflow"
4. Choose environment (testpypi or pypi)

### Q: Can I rollback a bad release?

A: Yes, yank the version on PyPI:
1. Go to PyPI project page
2. Click "History"
3. Select version → "Yank release"
4. Release a fixed version

### Q: What if I publish with wrong version?

A: You can't delete versions on PyPI, but you can:
1. Yank the wrong version (marks as unavailable)
2. Release correct version
3. Document issue in CHANGELOG

### Q: How long until package appears on PyPI?

A: Usually 5-10 minutes. PyPI caches and reindexes periodically.

### Q: Can I publish pre-release versions?

A: Yes, use version identifiers:
- `0.1.0a1` - Alpha release
- `0.1.0b1` - Beta release
- `0.1.0rc1` - Release candidate

These won't install by default unless explicitly requested.

## Resources

- **PyPI Package**: https://pypi.org/project/ennam-django-apidog/
- **Test PyPI**: https://test.pypi.org/project/ennam-django-apidog/
- **Release Guide**: [RELEASE.md](RELEASE.md)
- **Testing Guide**: [TESTING.md](TESTING.md)
- **Contributing**: [CLAUDE.md](CLAUDE.md)

## Support

For publishing issues:

1. Check GitHub Actions logs for detailed error messages
2. Review this guide and RELEASE.md
3. Check PyPI project settings and status
4. Review PyPI publishing documentation
5. Contact package maintainers if needed
