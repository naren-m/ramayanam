# End-to-End Testing Guide

This document provides comprehensive information about running E2E tests for the Ramayanam application.

## 🚀 Quick Start

### Local Development Testing
```bash
# Start your application first
python run.py

# Run E2E tests against local server
npm run test:e2e:local
```

### Docker Testing
```bash
# Build and test with Docker (full automation)
npm run test:e2e:docker

# Or use Docker Compose (recommended for CI)
npm run test:e2e:compose
```

## 📋 Prerequisites

- **Docker** and **Docker Compose** (for Docker-based testing)
- **Node.js** (v18 or higher)
- **npm** or **yarn**

## 🧪 Test Scripts Available

### 1. Local Development (`npm run test:e2e:local`)
- Tests against a locally running application
- Fastest execution time
- Best for development and debugging

```bash
# Basic usage
./scripts/test-e2e-local.sh

# With options
./scripts/test-e2e-local.sh --browser firefox --headed --port 3000
```

**Options:**
- `--port PORT`: Application port (default: 5000)
- `--browser NAME`: Browser choice (chromium|firefox|webkit)
- `--headed`: Show browser window
- `--ui`: Interactive test runner

### 2. Docker Container (`npm run test:e2e:docker`)
- Builds Docker image and runs tests against containerized app
- Tests production-like environment
- Includes automatic cleanup

```bash
# Full test suite
./scripts/test-e2e-docker.sh

# Build only
./scripts/test-e2e-docker.sh --build-only

# Show container logs
./scripts/test-e2e-docker.sh --logs
```

**Options:**
- `--no-cleanup`: Keep container running after tests
- `--build-only`: Only build Docker image
- `--logs`: Show container logs

### 3. Docker Compose (`npm run test:e2e:compose`)
- Uses docker-compose for service orchestration
- Includes health checks and proper service dependencies
- Best for CI/CD pipelines

```bash
# Full test suite
./scripts/test-e2e-compose.sh

# Show logs
./scripts/test-e2e-compose.sh --app-logs
./scripts/test-e2e-compose.sh --test-logs
```

### 4. Direct Playwright Commands
```bash
# Basic test run
npm run test:e2e

# Interactive UI mode
npm run test:e2e:ui

# Headed mode (visible browser)
npm run test:e2e:headed

# CI mode with GitHub reporter
npm run test:e2e:ci
```

## 📁 Test Structure

```
e2e/
├── search-functionality.spec.ts   # Search feature tests
├── ui-components.spec.ts          # UI component tests
└── api-integration.spec.ts        # API integration tests

scripts/
├── test-e2e-local.sh             # Local development testing
├── test-e2e-docker.sh            # Docker-based testing
└── test-e2e-compose.sh           # Docker Compose testing
```

## 🎯 Test Coverage

### Search Functionality
- ✅ English fuzzy search
- ✅ Sanskrit fuzzy search
- ✅ Empty query handling
- ✅ Kanda filtering
- ✅ Load more/pagination
- ✅ No results scenarios
- ✅ Search result clearing

### UI Components
- ✅ Header and navigation
- ✅ Theme toggling (dark/light)
- ✅ Search interface
- ✅ Loading states
- ✅ Verse card display
- ✅ Keyboard accessibility
- ✅ Responsive design

### API Integration
- ✅ API call verification
- ✅ Error handling
- ✅ Network connectivity issues
- ✅ Response validation
- ✅ Pagination testing
- ✅ Sanskrit vs English endpoints

## 🔧 Configuration

### Environment Variables
```bash
# Test configuration
export APP_PORT=5000              # Application port
export TEST_TIMEOUT=300           # Startup timeout (seconds)
export BASE_URL=http://localhost:5000  # Test target URL
```

### Playwright Configuration
The `playwright.config.ts` file includes:
- Cross-browser testing (Chromium, Firefox, WebKit)
- Automatic server startup
- Test timeouts and retries
- Screenshot and video capture on failure

## 🚀 CI/CD Integration

### GitHub Actions
The `.github/workflows/e2e-tests.yml` workflow:
- Runs on push/PR to main branches
- Tests across multiple browsers
- Uses Docker for consistent environment
- Uploads test artifacts and reports

### Running in CI
```bash
# CI-optimized command
CI=true npx playwright test --reporter=github
```

## 🐛 Debugging

### Local Debugging
```bash
# Run with visible browser
./scripts/test-e2e-local.sh --headed

# Interactive mode
./scripts/test-e2e-local.sh --ui

# Debug specific browser
./scripts/test-e2e-local.sh --browser firefox --headed
```

### Docker Debugging
```bash
# Show container logs
./scripts/test-e2e-docker.sh --logs

# Keep container running for inspection
./scripts/test-e2e-docker.sh --no-cleanup
```

### Test Reports
After running tests, view detailed reports:
```bash
# Open HTML report
npx playwright show-report

# View test artifacts
ls -la test-results/
ls -la playwright-report/
```

## 📊 Test Results

Tests generate several types of output:
- **Console output**: Real-time test progress
- **HTML reports**: Detailed test results with screenshots
- **Video recordings**: For failed tests (in headed mode)
- **Trace files**: For debugging test execution

## ⚠️ Troubleshooting

### Common Issues

1. **Application not starting**
   ```bash
   # Check if port is already in use
   lsof -i :5000
   
   # View application logs
   ./scripts/test-e2e-docker.sh --logs
   ```

2. **Browser installation issues**
   ```bash
   # Reinstall Playwright browsers
   npx playwright install --force
   ```

3. **Docker permission issues**
   ```bash
   # Add user to docker group (Linux)
   sudo usermod -aG docker $USER
   
   # Or run with sudo (not recommended)
   sudo ./scripts/test-e2e-docker.sh
   ```

4. **Test timeouts**
   ```bash
   # Increase timeout
   export TEST_TIMEOUT=600  # 10 minutes
   ```

### Performance Tips

1. **Use local testing during development**
   - Faster feedback loop
   - No Docker overhead

2. **Use Docker testing for integration**
   - Tests production environment
   - Catches deployment issues

3. **Parallel execution**
   ```bash
   # Run tests in parallel
   npx playwright test --workers=4
   ```

## 📚 Additional Resources

- [Playwright Documentation](https://playwright.dev/)
- [Docker Documentation](https://docs.docker.com/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

## 🤝 Contributing

When adding new tests:
1. Follow existing test patterns
2. Add appropriate `data-testid` attributes to UI components
3. Update this documentation
4. Test with all available browsers

---

For questions or issues, please check the troubleshooting section or open an issue in the repository.