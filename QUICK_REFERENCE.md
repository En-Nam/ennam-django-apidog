# Quick Reference - ennam-django-apidog v0.1.3

## Installation

```bash
pip install ennam-django-apidog
```

## Add to Django

```python
# settings.py
INSTALLED_APPS = [
    'rest_framework',
    'drf_spectacular',
    'ennam_django_apidog',
]

import os
APIDOG_SETTINGS = {
    'PROJECT_ID': os.getenv('APIDOG_PROJECT_ID'),
    'TOKEN': os.getenv('APIDOG_TOKEN'),
    'OUTPUT_DIR': os.path.join(BASE_DIR, 'apidog'),
}
```

## Using the Commands

### Linux/macOS

```bash
# Set environment variables
export APIDOG_PROJECT_ID=your-project-id
export APIDOG_TOKEN=your-api-token

# Export schema
python manage.py apidog export

# Validate schema
python manage.py apidog validate

# Push to APIDOG Cloud
python manage.py apidog push

# Pull from APIDOG Cloud
python manage.py apidog pull

# Compare schemas
python manage.py apidog compare

# Generate environment config
python manage.py apidog env-config
```

### Windows PowerShell

```powershell
# Set environment variables
[Environment]::SetEnvironmentVariable("APIDOG_PROJECT_ID", "your-project-id")
[Environment]::SetEnvironmentVariable("APIDOG_TOKEN", "your-api-token")

# Run commands
python manage.py apidog export
python manage.py apidog push
# ... etc
```

### Windows Command Prompt

```batch
set APIDOG_PROJECT_ID=your-project-id
set APIDOG_TOKEN=your-api-token

python manage.py apidog export
python manage.py apidog push
REM ... etc
```

## Important Note

⚠️ **Environment variables must be set in the SAME shell session before running commands.**

Running a separate script that sets variables will NOT work because the variables won't persist to the next command.

## All Commands

| Command | Purpose |
|---------|---------|
| `apidog init` | Initialize APIDOG directory structure |
| `apidog export` | Export OpenAPI schema from Django |
| `apidog validate` | Validate OpenAPI schema file |
| `apidog push` | Push schema to APIDOG Cloud |
| `apidog pull` | Pull schema from APIDOG Cloud |
| `apidog compare` | Compare local vs cloud schemas |
| `apidog env-config` | Generate environment configuration |

## Getting Help

### Understand Environment Variables

See: [ENVIRONMENT_VARIABLES_FIX.md](./ENVIRONMENT_VARIABLES_FIX.md)

### Error: "401 Unauthorized"

Cause: Environment variables not set
Solution: Set `APIDOG_PROJECT_ID` and `APIDOG_TOKEN` in shell before command

### Error: "403 Forbidden"

Cause: Token valid but lacks permissions
Solution: Use token from account with appropriate role in APIDOG

### Error: Module not found

```bash
pip install -e ".[dev]"
```

## Test Project

Complete working example in `test_django_project/`:

```bash
cd test_django_project

# See export commands for your platform
python load_env.py

# Copy one of the displayed commands, paste and run it
# Then:
python manage.py apidog push
```

## Documentation

- **README.md** - Complete feature overview
- **ENVIRONMENT_VARIABLES_FIX.md** - Detailed environment setup explanation
- **ENVIRONMENT_VARIABLES_GUIDE.md** - 401 error explanation
- **SESSION_SUMMARY.md** - This session's findings
- **TOKEN_VERIFICATION_TEST.md** - Token validation tests

## Quick Troubleshooting

| Problem | Check |
|---------|-------|
| Variables not recognized | Did you `export` or `set` them in current shell? |
| 401 Unauthorized | Are APIDOG_PROJECT_ID and APIDOG_TOKEN set? |
| 403 Forbidden | Is token role sufficient? Check APIDOG account settings |
| Schema export fails | Does Django have drf-spectacular configured? |

## Version Info

- **Latest Version**: 0.1.3
- **Python Support**: 3.8+
- **Django Support**: 3.2+
- **DRF Support**: 3.12+

## Support

Email: danny.tranhoang@ennam.vn
PyPI: https://pypi.org/project/ennam-django-apidog/

---

**Last Updated**: December 3, 2025
