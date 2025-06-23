#!/bin/bash

# Simple E2E Test Script for Local Development
# This script runs E2E tests against the local development server

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Default values
PORT=5000
BROWSER="chromium"
HEADED=false
UI_MODE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --port)
            PORT="$2"
            shift 2
            ;;
        --browser)
            BROWSER="$2"
            shift 2
            ;;
        --headed)
            HEADED=true
            shift
            ;;
        --ui)
            UI_MODE=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --port PORT       Port where the app is running (default: 5000)"
            echo "  --browser NAME    Browser to use (chromium|firefox|webkit, default: chromium)"
            echo "  --headed          Run tests in headed mode (visible browser)"
            echo "  --ui              Run tests in UI mode (interactive)"
            echo "  --help, -h        Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                          # Run tests against localhost:5000"
            echo "  $0 --port 3000             # Run tests against localhost:3000"
            echo "  $0 --browser firefox       # Use Firefox browser"
            echo "  $0 --headed                # Show browser window"
            echo "  $0 --ui                     # Interactive mode"
            echo ""
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Check if application is running
check_app() {
    print_status "Checking if application is running on port ${PORT}..."
    
    if curl -s -f "http://localhost:${PORT}/" >/dev/null; then
        print_success "Application is running on port ${PORT}"
        return 0
    else
        print_error "Application is not running on port ${PORT}"
        print_status "Please start your application first:"
        echo "  # For local development:"
        echo "  python run.py"
        echo ""
        echo "  # For Docker:"
        echo "  docker run -p ${PORT}:5000 ramayanam"
        echo ""
        return 1
    fi
}

# Install dependencies if needed
install_deps() {
    if [ ! -d "node_modules" ] || [ ! -f "node_modules/.bin/playwright" ]; then
        print_status "Installing dependencies..."
        npm install
    fi
    
    # Check if Playwright browsers are installed
    if ! npx playwright --version >/dev/null 2>&1; then
        print_status "Installing Playwright browsers..."
        npx playwright install
    fi
}

# Run tests
run_tests() {
    print_status "Running E2E tests..."
    
    # Build command
    local cmd="npx playwright test"
    
    if [ "$BROWSER" != "all" ]; then
        cmd="$cmd --project=$BROWSER"
    fi
    
    if [ "$HEADED" = true ]; then
        cmd="$cmd --headed"
    fi
    
    if [ "$UI_MODE" = true ]; then
        cmd="$cmd --ui"
    fi
    
    cmd="$cmd --reporter=line"
    
    print_status "Running: $cmd"
    
    # Set base URL for tests
    export PLAYWRIGHT_BASE_URL="http://localhost:${PORT}"
    
    # Update playwright config temporarily
    if [ -f "playwright.config.ts" ]; then
        sed -i.bak "s|baseURL: '[^']*'|baseURL: 'http://localhost:${PORT}'|g" playwright.config.ts
        sed -i.bak "s|command: 'python run.py'|command: 'echo \"Using existing server\"'|g" playwright.config.ts
        sed -i.bak "s|reuseExistingServer: !process.env.CI|reuseExistingServer: true|g" playwright.config.ts
    fi
    
    # Run the tests
    if eval "$cmd"; then
        print_success "E2E tests completed successfully!"
        TEST_RESULT=0
    else
        print_warning "Some E2E tests failed"
        TEST_RESULT=1
    fi
    
    # Restore original config
    if [ -f "playwright.config.ts.bak" ]; then
        mv playwright.config.ts.bak playwright.config.ts
    fi
    
    return $TEST_RESULT
}

# Main execution
main() {
    echo "🧪 Running E2E Tests Locally"
    echo "============================="
    echo "Port: ${PORT}"
    echo "Browser: ${BROWSER}"
    echo "Headed: ${HEADED}"
    echo "UI Mode: ${UI_MODE}"
    echo ""
    
    # Check if app is running
    if ! check_app; then
        exit 1
    fi
    
    # Install dependencies
    install_deps
    
    # Run tests
    if run_tests; then
        print_success "🎉 All tests completed!"
        
        # Show test report if available
        if [ -d "playwright-report" ] && [ "$UI_MODE" = false ]; then
            print_status "Test report available at: npx playwright show-report"
        fi
    else
        print_warning "⚠️  Some tests failed - check the output above"
        exit 1
    fi
}

# Run main function
main