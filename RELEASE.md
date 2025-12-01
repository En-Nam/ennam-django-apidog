# Release Guide for ennam-django-apidog

This document outlines the process for releasing new versions of the ennam-django-apidog package.

## Pre-Release Checklist

Before creating a release, ensure the following:

### 1. Code Quality

- [ ] All tests pass locally
  ```bash
  pytest
  ```

- [ ] All tests pass on CI/CD
  - Check GitHub Actions workflow status
  - All Python 3.8-3.12 versions passing
  - All Django 3.2-5.0 versions passing

- [ ] No type errors
  ```bash
  mypy src/ --strict
  ```

- [ ] No linting errors
  ```bash
  ruff check src/ tests/
  ```

- [ ] Code formatted correctly
  ```bash
  ruff format src/ tests/
  ```

- [ ] Pre-commit hooks pass
  ```bash
  pre-commit run --all-files
  ```

### 2. Test Coverage

- [ ] Coverage is at least 40-50%
  ```bash
  pytest --cov=src --cov-report=html
  ```

- [ ] All critical paths tested
  - HTTP API interactions (push, pull, compare)
  - Management commands (export, validate, init)
  - Settings and configuration
  - Error handling and edge cases

### 3. Documentation

- [ ] README.md is up to date
  - Installation instructions correct
  - Usage examples working
  - Testing section complete

- [ ] TESTING.md reflects current test suite
  - Test structure documented
  - All test categories listed
  - Running instructions accurate

- [ ] CLAUDE.md has project guidance
  - Architecture documented
  - Key implementation details noted
  - Development tasks explained

- [ ] CHANGELOG entries prepared
  - New features documented
  - Bug fixes listed
  - Breaking changes noted (if any)

- [ ] Docstrings are complete
  - All public functions documented
  - Examples included where appropriate

### 4. Version Management

- [ ] Version bumped in `pyproject.toml`
  ```toml
  version = "X.Y.Z"
  ```

  Follow semantic versioning:
  - MAJOR.MINOR.PATCH (e.g., 0.1.0, 1.0.0)
  - 0.x.y: Pre-release versions
  - 1.0.0: First stable release
  - Breaking changes: bump MAJOR
  - New features: bump MINOR
  - Bug fixes: bump PATCH

- [ ] Git tag created with version
  ```bash
  git tag -a vX.Y.Z -m "Release version X.Y.Z"
  git push origin vX.Y.Z
  ```

- [ ] Commit message clear and descriptive
  ```bash
  git add .
  git commit -m "chore: release version X.Y.Z"
  ```

### 5. Compatibility Verification

- [ ] Package installs correctly
  ```bash
  pip install -e .
  ```

- [ ] All dependencies available
  ```bash
  pip install -e ".[dev]"
  ```

- [ ] Import works without errors
  ```python
  import ennam_django_apidog
  ```

- [ ] Management command available
  ```bash
  python manage.py apidog --help
  ```

### 6. Build and Distribution

- [ ] Distribution builds without errors
  ```bash
  python -m build
  ```

- [ ] Distribution passes checks
  ```bash
  twine check dist/*
  ```

- [ ] Wheel and source distributions created
  ```bash
  ls -lh dist/
  # Should show both .whl and .tar.gz files
  ```

## Release Process

### Step 1: Create GitHub Release

1. Go to GitHub repository
2. Click "Releases" → "Draft a new release"
3. Create tag: `vX.Y.Z`
4. Release title: `Release version X.Y.Z`
5. Add release notes with:
   - Summary of changes
   - Features added
   - Bugs fixed
   - Known issues (if any)
6. Click "Publish release"

### Step 2: Automated Publishing

The GitHub Actions workflow will automatically:

1. **Build**: Create wheel and source distributions
2. **Test Build**: Verify package integrity
3. **Publish to TestPyPI**: Upload to test repository
4. **Test TestPyPI**: Verify test installation works
5. **Publish to PyPI**: Upload to production PyPI (if not a pre-release)
6. **Verify**: Confirm package is available on PyPI

### Step 3: Manual Verification (Optional)

If publishing manually or for verification:

```bash
# Install test package
pip install --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ \
  ennam-django-apidog

# Install production package
pip install ennam-django-apidog

# Verify version
python -c "import ennam_django_apidog; print('Package installed')"
```

### Step 4: Announce Release

- [ ] Update GitHub release notes with PyPI link
- [ ] Share release on relevant channels
  - Python community forums
  - Django community
  - APIDOG channels (if applicable)

## Version Numbering

### Current Version: 0.1.0 (Beta)

- **0.1.x**: Pre-release versions with API stabilization
  - Features may change between releases
  - Not recommended for production use yet
  - Full test coverage expected

- **1.0.0**: First stable release
  - API stabilization complete
  - Full backward compatibility maintained
  - Production-ready

### When to Release

Release a new version when:

- [ ] New features are complete and tested
- [ ] Bugs are fixed and verified
- [ ] Documentation is updated
- [ ] All tests pass

Recommended cadence:
- **Beta (0.x.y)**: Every 2-4 weeks as features stabilize
- **Stable (1.x.y+)**: Monthly or as-needed for bug fixes

## Troubleshooting

### Build Fails

```bash
# Clean old builds
rm -rf build/ dist/ *.egg-info/

# Rebuild
python -m build

# Check for errors
twine check dist/*
```

### PyPI Upload Fails

1. Verify credentials are set up correctly
2. Check that version hasn't been released before
3. Ensure distribution files pass checks

### TestPyPI Upload Succeeds but PyPI Fails

1. Verify you have PyPI account setup
2. Check that token/credentials are valid
3. Ensure version number is unique on PyPI

### Package Doesn't Install from PyPI

1. Wait 5-10 minutes for PyPI to index the package
2. Clear pip cache: `pip cache purge`
3. Try installing again: `pip install --no-cache-dir ennam-django-apidog`

## Rollback Plan

If a bad release is published:

1. **Yanking a Version**
   - Go to PyPI project settings
   - Click "History" → select version
   - Click "Options" → "Yank release"
   - Users will get a warning when installing yanked version

2. **New Patch Release**
   - Fix the issue
   - Bump patch version (e.g., 0.1.1 → 0.1.2)
   - Release as normal

3. **Communicate**
   - Update GitHub release notes
   - Notify users in documentation

## Security Considerations

- [ ] No credentials committed to repository
- [ ] No API tokens in code
- [ ] No hardcoded secrets in configuration
- [ ] Dependencies are vetted (no malicious packages)
- [ ] No binary files in source distribution

## Post-Release

- [ ] Monitor PyPI downloads and feedback
- [ ] Watch GitHub issues for problems
- [ ] Update version in `pyproject.toml` for next development cycle
  ```toml
  version = "X.Y.Z-dev"
  ```

- [ ] Plan next release milestones

## Resources

- [PyPI Publishing Guide](https://packaging.python.org/tutorials/packaging-projects/)
- [Semantic Versioning](https://semver.org/)
- [GitHub Actions for PyPI](https://github.com/pypa/gh-action-pypi-publish)
- [Twine Documentation](https://twine.readthedocs.io/)

## Support

For release issues or questions:

1. Review this guide
2. Check GitHub Actions logs
3. Review PyPI project settings
4. Contact package maintainers
