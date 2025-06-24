# Claude Code Session Notes

## Project: Ramayanam Digital Corpus

### Testing Infrastructure

#### E2E Testing Scripts

**Docker-based E2E Testing:**
- `scripts/test-e2e-docker.sh` - **Requires Docker** - Builds Docker image and runs E2E tests against containerized app
- `scripts/test-e2e-compose.sh` - **Requires Docker** - Uses Docker Compose for orchestrated testing environment

**Local E2E Testing:**
- `scripts/test-e2e-local.sh` - **No Docker required** - Runs E2E tests against existing local server
  - Usage: Start your app locally first (`python run.py`) then run the script
  - Supports various options: `--port`, `--browser`, `--headed`, `--ui`

#### Backend Testing Scripts

**Backend Testing:**
- `scripts/test-backend.sh` - **No Docker required** - Comprehensive pytest testing suite
  - Creates virtual environment automatically
  - Installs test dependencies from `requirements-test.txt`
  - Supports multiple test types: unit, integration, api, service, model, performance
  - Generates coverage reports and HTML documentation
  - Usage: `./scripts/test-backend.sh [all|unit|integration|api|service|model|performance|parallel]`

#### Test Configuration Files

- `playwright.config.ts` - Playwright E2E test configuration
- `pytest.ini` - pytest configuration with coverage settings
- `requirements-test.txt` - Python testing dependencies
- `conftest.py` - pytest fixtures and test configuration

#### Test Suites Created

**E2E Tests (Playwright):**
- `e2e/search-functionality.spec.ts` - Search, pagination, filtering tests
- `e2e/ui-components.spec.ts` - UI component and accessibility tests
- `e2e/api-integration.spec.ts` - API integration tests

**Backend Tests (pytest):**
- `tests/unit/test_api_endpoints.py` - API endpoint testing
- `tests/unit/test_models.py` - Model validation tests
- `tests/unit/test_services.py` - Service layer tests with mocking
- `tests/integration/test_api_integration.py` - Full workflow integration tests

### Quick Testing Commands

```bash
# Backend testing (no Docker)
./scripts/test-backend.sh           # All tests with coverage
./scripts/test-backend.sh unit      # Unit tests only
./scripts/test-backend.sh model     # Model tests only (✅ passing)
./scripts/test-backend.sh parallel  # Parallel execution

# E2E testing - Local (no Docker)
python run.py                       # Start app first
./scripts/test-e2e-local.sh         # Run E2E tests

# E2E testing - Docker (requires Docker)
./scripts/test-e2e-docker.sh        # Build image and test
./scripts/test-e2e-compose.sh       # Docker Compose testing
```

### Testing Status

**✅ Working:**
- Configuration fixed for local development (data path auto-detection)
- Model tests (23/23 passing) - Sloka class with proper `__repr__`, `__eq__`, `__hash__`
- Test infrastructure and script execution

**⚠️ Needs Work:**
- Some API endpoint tests (integration issues)
- Service layer tests (mock data compatibility)
- End-to-end integration tests