# Comprehensive Testing Guide

This document outlines the consolidated testing infrastructure for the Ramayanam project, organized into 3 distinct categories for optimal test management and execution.

## 🎯 Test Categories

### 1. **Unit Tests** (pytest API level)
- **Purpose:** Test individual components, functions, and API endpoints in isolation
- **Framework:** pytest with mocking and fixtures
- **Location:** `tests/unit/`
- **Speed:** Fast (< 1 second per test)
- **Dependencies:** None (fully isolated with mocks)

### 2. **End-to-End Tests** (pytest API integration)
- **Purpose:** Test complete API workflows and data integration
- **Framework:** pytest with real API calls
- **Location:** `tests/integration/`
- **Speed:** Medium (1-5 seconds per test)
- **Dependencies:** Running application API

### 3. **UI Tests** (Playwright)
- **Purpose:** Test user interface, user interactions, and frontend functionality
- **Framework:** Playwright with TypeScript
- **Location:** `tests/e2e/`
- **Speed:** Slow (5-30 seconds per test)
- **Dependencies:** Running application with UI

## 🚀 Quick Start

### Run All Tests
```bash
# Run complete test suite
npm test

# Or using the script directly
./run-all-tests.sh all
```

### Run Specific Test Categories
```bash
# Unit tests only (fastest)
npm run test:unit

# End-to-end API tests
npm run test:e2e

# UI tests  
npm run test:ui

# Performance tests
npm run test:performance
```

### Run with Options
```bash
# Force rebuild containers
npm run test:build

# Run tests and start report server
npm run test:reports

# Local UI testing (no Docker)
npm run test:ui:local
```

## 🐳 Docker-Based Testing

All tests run in Docker containers for consistency and isolation.

### Architecture
- **app:** Main application service (port 5000)
- **test-runner:** Comprehensive test executor
- **unit-tests:** Isolated unit test runner
- **e2e-tests:** API integration test runner  
- **ui-tests:** Playwright UI test runner
- **report-server:** Nginx server for test reports (port 8080)

### Docker Commands
```bash
# Run all tests
docker-compose -f docker-compose.tests.yml run --rm test-runner

# Run specific category
docker-compose -f docker-compose.tests.yml run --rm unit-tests
docker-compose -f docker-compose.tests.yml run --rm e2e-tests
docker-compose -f docker-compose.tests.yml run --rm ui-tests

# Start report server
docker-compose -f docker-compose.tests.yml up report-server
```

## 📊 Test Reports

### Accessing Reports
After running tests, reports are available at:
- **Local:** `./reports/` directory
- **Web Server:** http://localhost:8080 (when using `--reports` flag)

### Report Types
- **Unit Coverage:** HTML coverage reports with line-by-line analysis
- **E2E Coverage:** API integration coverage reports
- **UI Results:** Playwright HTML reports with screenshots and videos
- **Performance:** JSON benchmark results
- **JUnit XML:** CI/CD compatible test results

## 🏗️ Test Structure

```
tests/
├── unit/                   # Unit Tests (pytest)
│   ├── test_models.py     # Data model tests
│   ├── test_api_endpoints.py # API endpoint tests
│   ├── test_services.py   # Service layer tests
│   └── test_fuzzy_search_service.py # Search service tests
├── integration/           # End-to-End Tests (pytest)
│   ├── test_api_integration.py # Full API workflow tests
│   └── test_data_integration.py # Data integration tests
├── e2e/                   # UI Tests (Playwright)
│   ├── search-functionality.spec.ts # Search feature tests
│   ├── ui-components.spec.ts # UI component tests
│   └── api-integration.spec.ts # API integration via UI
├── performance/           # Performance Tests
│   ├── test_search_performance.py # Search benchmarks
│   └── performance_metrics.json # Metrics storage
└── conftest.py           # Shared pytest fixtures
```

## ⚙️ Configuration Files

- **pytest.tests.ini:** Comprehensive pytest configuration
- **playwright.config.ts:** Playwright test configuration
- **docker-compose.tests.yml:** Test orchestration
- **Dockerfile.tests:** Multi-stage test container
- **nginx-test-reports.conf:** Report server configuration

## 🔧 Development Workflow

### Adding New Tests

**Unit Tests:**
```python
# tests/unit/test_new_feature.py
import pytest
from api.services import new_feature_service

@pytest.mark.unit
def test_new_feature():
    result = new_feature_service.process()
    assert result is not None
```

**End-to-End Tests:**
```python
# tests/integration/test_new_api.py
import pytest
import requests

@pytest.mark.integration
def test_new_api_endpoint():
    response = requests.get("http://app:5000/api/new-endpoint")
    assert response.status_code == 200
```

**UI Tests:**
```typescript
// tests/e2e/new-feature.spec.ts
import { test, expect } from '@playwright/test';

test('should test new UI feature', async ({ page }) => {
  await page.goto('/');
  await expect(page.locator('[data-testid="new-feature"]')).toBeVisible();
});
```

### Test Markers
Use pytest markers to categorize tests:
```python
@pytest.mark.unit        # Unit test
@pytest.mark.integration # Integration test
@pytest.mark.slow        # Slow test
@pytest.mark.critical    # Critical functionality
@pytest.mark.smoke       # Smoke test
```

## 🚀 CI/CD Integration

### GitHub Actions Example
```yaml
name: Test Suite
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Tests
        run: ./run-all-tests.sh all
      - name: Upload Reports
        uses: actions/upload-artifact@v3
        with:
          name: test-reports
          path: reports/
```

### Running in CI
```bash
# CI-optimized execution
CI=true ./run-all-tests.sh all --build
```

## 📈 Performance Testing

### Benchmarks
```bash
# Run performance tests only
npm run test:performance

# View results
cat reports/performance.json
```

### Metrics Tracked
- API response times
- Database query performance
- Search algorithm efficiency
- Memory usage patterns
- Concurrent request handling

## 🐛 Debugging

### Local Development
```bash
# Debug UI tests with browser
npm run test:ui:headed

# Run specific test file
playwright test tests/e2e/search-functionality.spec.ts --debug

# Unit tests with verbose output
pytest tests/unit/test_models.py -v -s
```

### Container Debugging
```bash
# Access test container
docker-compose -f docker-compose.tests.yml run --rm test-runner bash

# View logs
docker-compose -f docker-compose.tests.yml logs app
```

## 📋 Test Checklist

Before committing code, ensure:
- [ ] All unit tests pass
- [ ] Integration tests pass with real API
- [ ] UI tests pass with current interface
- [ ] Performance benchmarks are within acceptable limits
- [ ] Test coverage meets minimum threshold (70%)
- [ ] New features include appropriate tests

## 🆘 Troubleshooting

### Common Issues

**Docker not starting:**
```bash
# Check Docker status
docker info

# Clean up old containers
docker-compose -f docker-compose.tests.yml down --volumes
```

**Port conflicts:**
```bash
# Check for running services
lsof -i :5000 -i :8080

# Use different ports
export APP_PORT=5001
```

**Browser issues (UI tests):**
```bash
# Reinstall browsers
npx playwright install --force
```

**Test timeouts:**
```bash
# Increase timeouts in playwright.config.ts
timeout: 60000  // 60 seconds
```

## 🤝 Contributing

When adding new tests:
1. Choose the appropriate test category
2. Follow existing naming conventions
3. Add proper test markers
4. Update this documentation
5. Ensure tests are deterministic and isolated

---

For questions or issues, refer to the troubleshooting section or open an issue in the repository.