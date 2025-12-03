# Environment Variables Configuration Guide

## Issue Explanation: 401 Error

The 401 (Unauthorized) error occurred when environment variables were set but not being read correctly due to **key mapping mismatch**.

## How Environment Variables Work

### 1. Settings Hierarchy (Priority Order)

The package follows this priority order when reading credentials:

```
1. Command-line arguments (highest)
   └─ python manage.py apidog push --project-id=123 --token=xxx

2. Django APIDOG_SETTINGS (settings.py)
   └─ APIDOG_SETTINGS = {'PROJECT_ID': '123', 'TOKEN': 'xxx'}

3. Environment variables
   └─ export APIDOG_PROJECT_ID=123
   └─ export APIDOG_TOKEN=xxx

4. Defaults (lowest)
   └─ None
```

### 2. Environment Variable Mapping

The package maps **internal attribute names** to **environment variable names**:

```python
# src/ennam_django_apidog/settings.py
# __getattr__ method (lines 88-109)

def __getattr__(self, attr: str) -> Any:
    if attr == "PROJECT_ID":
        val = os.environ.get("APIDOG_PROJECT_ID", self.defaults[attr])
    elif attr == "TOKEN":
        val = os.environ.get("APIDOG_TOKEN", self.defaults[attr])
    elif attr == "OUTPUT_DIR":
        val = os.environ.get("APIDOG_OUTPUT_DIR", self.defaults[attr])
```

**Mapping:**
- Internal: `PROJECT_ID` → Environment: `APIDOG_PROJECT_ID`
- Internal: `TOKEN` → Environment: `APIDOG_TOKEN`
- Internal: `OUTPUT_DIR` → Environment: `APIDOG_OUTPUT_DIR`

## The Problem We Encountered

### What Happened Yesterday

1. **Test project had hardcoded dummy values:**
   ```python
   # test_django_project/project/settings.py
   APIDOG_SETTINGS = {
       'PROJECT_ID': 'test-project-id',      # ❌ Dummy value
       'TOKEN': 'test-api-token',            # ❌ Dummy value
       'OUTPUT_DIR': os.path.join(BASE_DIR, 'apidog'),
   }
   ```

2. **Environment variables were set:**
   ```bash
   export APIDOG_PROJECT_ID=1133189
   export APIDOG_TOKEN=APS-CEkL8JPRJPeLojA3zc3MrcjDUo4rRBIT
   ```

3. **But Django settings took precedence:**
   ```
   get_credentials() returned:
   - project_id = 'test-project-id'  (from Django settings)
   - token = 'test-api-token'        (from Django settings)
   ```

4. **API call with dummy credentials:**
   ```
   POST /projects/test-project-id/import-openapi
   Authorization: Bearer test-api-token
   
   Result: 401 Unauthorized ❌
   ```

### The Root Cause

**Django settings `APIDOG_SETTINGS` dictionary has higher priority than environment variables.**

Looking at the code in `settings.py` lines 88-91:

```python
def __getattr__(self, attr: str) -> Any:
    # Check user settings FIRST
    try:
        val = self.user_settings[attr]  # ← This is Django APIDOG_SETTINGS
    except KeyError:
        # Only check env vars if NOT in Django settings
        if attr == "PROJECT_ID":
            val = os.environ.get("APIDOG_PROJECT_ID", ...)
```

**Priority in code:**
1. Django `APIDOG_SETTINGS` dictionary (checked first)
2. Environment variables (fallback)

## The Solution

### Fix Applied

Updated `test_django_project/project/settings.py` to read from environment variables:

```python
import os

APIDOG_SETTINGS = {
    'PROJECT_ID': os.getenv('APIDOG_PROJECT_ID', '1133189'),
    'TOKEN': os.getenv('APIDOG_TOKEN', 'test-api-token'),
    'OUTPUT_DIR': os.path.join(BASE_DIR, 'apidog'),
}
```

Now the priority is:
1. Environment variables (via `os.getenv()`)
2. Fallback defaults
3. Django reads environment at startup

## Best Practice

### For Development (Local Machine)

Create `.env.local` file:
```
APIDOG_PROJECT_ID=1133189
APIDOG_TOKEN=your-token-here
```

Then in Django settings:
```python
import os
from pathlib import Path

# Load .env variables
from dotenv import load_dotenv
load_dotenv('.env.local')

APIDOG_SETTINGS = {
    'PROJECT_ID': os.getenv('APIDOG_PROJECT_ID'),
    'TOKEN': os.getenv('APIDOG_TOKEN'),
    'OUTPUT_DIR': os.path.join(BASE_DIR, 'apidog'),
}
```

### For Production (CI/CD)

Set environment variables in CI/CD platform:
```bash
# GitHub Actions, GitLab CI, etc.
export APIDOG_PROJECT_ID=${{ secrets.APIDOG_PROJECT_ID }}
export APIDOG_TOKEN=${{ secrets.APIDOG_TOKEN }}
```

Then in Django settings:
```python
APIDOG_SETTINGS = {
    'PROJECT_ID': os.getenv('APIDOG_PROJECT_ID'),
    'TOKEN': os.getenv('APIDOG_TOKEN'),
    'OUTPUT_DIR': os.path.join(BASE_DIR, 'apidog'),
}
```

### For Direct Configuration

```python
# Hardcoded (less secure)
APIDOG_SETTINGS = {
    'PROJECT_ID': '1133189',
    'TOKEN': 'your-token',
    'OUTPUT_DIR': 'apidog',
}
```

## Summary

| Method | Pros | Cons | Use Case |
|--------|------|------|----------|
| Environment Variables | Secure, flexible | Requires setup | Production, CI/CD |
| Django Settings + os.getenv() | Clean, readable | Still readable code | Recommended for all |
| Hardcoded | Simple | Insecure, not flexible | Development only |

**The issue was:** Django settings had hardcoded dummy values that took priority over environment variables.

**The fix:** Use `os.getenv()` in Django settings to read from environment variables instead of hardcoding them.

**Key Takeaway:** When using environment variables, always read them in Django settings using `os.getenv()`, not as hardcoded values in `APIDOG_SETTINGS`.
