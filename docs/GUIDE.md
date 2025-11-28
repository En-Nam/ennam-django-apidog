# APIDOG Integration Guide

## Table of Contents
- [Overview](#overview)
- [Getting Started](#getting-started)
- [For Developers](#for-developers)
- [For QA Team](#for-qa-team)
- [For Frontend/Mobile Team](#for-frontendmobile-team)
- [Environment Management](#environment-management)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Overview

APIDOG is a centralized API documentation and testing platform that replaces multiple tools (Postman, Swagger, etc.) with a single, integrated solution. This package (`ennam-django-apidog`) provides seamless integration between Django REST Framework and APIDOG.

### Key Benefits
- **Real-time API synchronization** with Django backend
- **Easy environment switching** (Local, Dev, Staging, Prod)
- **Auto-generated documentation** always up-to-date
- **Integrated testing** with AI-powered test generation
- **Team collaboration** with real-time updates

## Getting Started

### 1. Installation

```bash
pip install ennam-django-apidog
```

### 2. Django Configuration

Add to your `settings.py`:

```python
INSTALLED_APPS = [
    ...
    'rest_framework',
    'drf_spectacular',
    'ennam_django_apidog',
]

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Your API',
    'DESCRIPTION': 'API Description',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SCHEMA_PATH_PREFIX': r'/api/',
    'SERVERS': [
        {'url': 'http://localhost:8000', 'description': 'Local'},
        {'url': 'https://api.yourapp.com', 'description': 'Production'},
    ],
}
```

### 3. URL Configuration

Add to your `urls.py`:

```python
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    ...
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
```

### 4. APIDOG Configuration

```python
# settings.py
APIDOG_SETTINGS = {
    'PROJECT_ID': 'your-project-id',
    'TOKEN': 'your-api-token',
    'ENVIRONMENTS': {
        'local': {
            'name': 'Local Development',
            'base_url': 'http://localhost:8000',
        },
        'staging': {
            'name': 'Staging',
            'base_url': 'https://staging.yourapp.com',
        },
        'production': {
            'name': 'Production',
            'base_url': 'https://api.yourapp.com',
        },
    },
}
```

### 5. Initialize Project

```bash
python manage.py apidog init
```

This creates:
- `apidog/` directory with README
- `Makefile.apidog` for shortcut commands
- `docker-compose.apidog.yml` for mock server
- `.gitignore` rules for generated files

## For Developers

### Exporting API Schema

```bash
# Export as JSON (default)
python manage.py apidog export

# Export as YAML
python manage.py apidog export --format yaml

# Custom output directory
python manage.py apidog export --output /path/to/output/

# Validate exported schema
python manage.py apidog validate

# Compare local vs cloud
python manage.py apidog compare

# Push to APIDOG Cloud
python manage.py apidog push

# Pull from APIDOG Cloud
python manage.py apidog pull

# Generate environment config
python manage.py apidog env-config
```

### Docker Usage

```bash
docker-compose exec web python manage.py apidog export
docker-compose exec web python manage.py apidog compare
docker-compose exec web python manage.py apidog push
```

### Importing to APIDOG

1. **Manual Import**
   - Click `Settings` → `Import Data`
   - Select `OpenAPI/Swagger`
   - Upload `apidog/openapi_schema_latest.json`
   - Choose `Smart Merge` to preserve existing data
   - Click `Import`

2. **URL Import** (After deployment)
   - Use URL: `https://your-domain.com/api/schema/`
   - Set up scheduled import for automatic updates

### Testing Your APIs

```javascript
// Example test script
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response has required fields", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('id');
    pm.expect(jsonData).to.have.property('status');
});
```

### Working with Mock Servers

```bash
# Start mock server
docker-compose -f docker-compose.apidog.yml up -d apidog-mock

# Mock server available at http://localhost:4010
```

```javascript
// In your app config
const API_BASE_URL = process.env.NODE_ENV === 'development'
  ? 'http://localhost:4010'  // APIDOG mock
  : 'https://api.yourapp.com';  // Production
```

## For QA Team

### Running Test Suites

1. **Access Test Collections**
   - Click `Test` in sidebar
   - Find test collections:
     - Authentication Tests
     - API Flow Tests
     - Performance Tests

2. **Execute Tests**
   - Select test collection
   - Choose environment
   - Click `Run`
   - View results in real-time

3. **Data-Driven Testing**
   - Upload CSV/JSON test data
   - Map data to variables
   - Run tests with multiple datasets

### Creating Bug Reports

When test fails:
- Click failed test
- Copy shareable link
- Include in bug report:
  - Test name
  - Environment
  - Expected vs Actual
  - APIDOG link

## For Frontend/Mobile Team

### Using API Documentation

1. **Browse APIs**
   - Navigate through folders
   - View endpoint details
   - See request/response examples

2. **Try It Out**
   - Click `Try it Out` button
   - Modify parameters
   - Send request
   - Copy response for mocking

### Generating SDK Code

1. **Code Generation**
   - Click `Code` button on endpoint
   - Select language/framework:
     - JavaScript/Axios
     - TypeScript
     - React Query
     - Swift
     - Kotlin
   - Copy generated code

```typescript
// Example: TypeScript with Axios
interface CreateRequest {
  name: string;
  email: string;
}

async function createItem(data: CreateRequest) {
  const response = await axios.post(
    `${BASE_URL}/api/v1/items`,
    data,
    {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    }
  );
  return response.data;
}
```

## Environment Management

### Environment Variables

| Variable | Description | Source |
|----------|-------------|--------|
| `auth_token` | JWT access token | POST `/api/v1/login/` |
| `refresh_token` | JWT refresh token | POST `/api/v1/login/` |

### Switching Environments

```bash
# Local testing
Environment: Local Development
Base URL: http://localhost:8000

# Integration testing
Environment: Development Server
Base URL: https://dev.yourapp.com

# User acceptance testing
Environment: Staging
Base URL: https://staging.yourapp.com
```

## Best Practices

### 1. API Design
- Follow RESTful conventions
- Use consistent naming (camelCase for JSON)
- Version your APIs (`/api/v1/`)
- Document all parameters

### 2. Testing
- Write tests for all critical paths
- Use environment variables, not hardcoded values
- Test error scenarios
- Include performance benchmarks

### 3. Documentation
- Add descriptions to all endpoints
- Include example requests/responses
- Document error codes
- Keep schemas updated

### 4. Collaboration
- Use descriptive folder structure
- Tag APIs appropriately
- Share links instead of screenshots
- Comment on API changes

### 5. Security
- Never commit tokens to git
- Use environment variables for sensitive data
- Rotate tokens regularly
- Restrict production access

## Troubleshooting

### Common Issues

#### 1. Authentication Failed
```
Error: 401 Unauthorized
```
**Solution:**
- Check if token expired
- Refresh token via `/api/v1/refresh/`
- Update `auth_token` in environment

#### 2. Schema Export Failed
```
Error: Failed to fetch schema
```
**Solution:**
- Verify drf-spectacular is installed: `pip show drf-spectacular`
- Check URL route: `curl http://localhost:8000/api/schema/`
- Check Django settings configuration

#### 3. Push to APIDOG Failed
```
Error: 401 Unauthorized
```
**Solution:**
- Verify `APIDOG_TOKEN` is correct
- Check token permissions in APIDOG dashboard
- Regenerate token if needed

#### 4. Import Failed
```
Error: Invalid OpenAPI schema
```
**Solution:**
- Validate schema first: `python manage.py apidog validate`
- Check for syntax errors
- Update drf-spectacular version

### Getting Help

1. **Package Issues**
   - [GitHub Issues](https://github.com/ennam/ennam-django-apidog/issues)

2. **APIDOG Support**
   - [Documentation](https://docs.apidog.com)
   - [Community Forum](https://community.apidog.com)

3. **Django/DRF Issues**
   - Check Django logs
   - Verify drf-spectacular config
   - Test endpoint manually first

## CI/CD Integration

### GitHub Actions Example

```yaml
name: APIDOG Sync

on:
  push:
    branches: [main]
    paths:
      - 'app/**/*.py'

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.10'

    - name: Install dependencies
      run: pip install -r requirements.txt

    - name: Export Schema
      run: python manage.py apidog export
      env:
        DJANGO_SETTINGS_MODULE: yourapp.settings

    - name: Push to APIDOG
      run: python manage.py apidog push
      env:
        APIDOG_PROJECT_ID: ${{ secrets.APIDOG_PROJECT_ID }}
        APIDOG_TOKEN: ${{ secrets.APIDOG_TOKEN }}
```

## Quick Commands Reference

```bash
# Django Management Commands
python manage.py apidog init           # Initialize project
python manage.py apidog export         # Export schema
python manage.py apidog validate       # Validate schema
python manage.py apidog push           # Push to cloud
python manage.py apidog pull           # Pull from cloud
python manage.py apidog compare        # Compare local vs cloud
python manage.py apidog env-config     # Generate env config

# Makefile Commands
make -f Makefile.apidog export         # Export schema
make -f Makefile.apidog push           # Push to cloud
make -f Makefile.apidog sync           # Export + push
make -f Makefile.apidog compare        # Compare
make -f Makefile.apidog clean          # Clean generated files
```

---

*For more information, visit [APIDOG Documentation](https://docs.apidog.com)*
