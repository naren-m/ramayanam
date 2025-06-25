#!/bin/bash

# Knowledge Graph Automated Test Suite
# Runs comprehensive tests for both API and UI components

set -e  # Exit on any error

# Configuration
API_URL="${API_URL:-http://localhost:8080}"
UI_URL="${UI_URL:-http://localhost:3000}"
BACKEND_CONTAINER="${BACKEND_CONTAINER:-ramayanam-ramayanam-kg-1}"
TEST_TIMEOUT="${TEST_TIMEOUT:-60}"
HEADLESS="${HEADLESS:-true}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if a service is running
check_service() {
    local url=$1
    local name=$2
    local max_attempts=30
    local attempt=1
    
    log_info "Checking if $name is running at $url..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s -f "$url" > /dev/null 2>&1; then
            log_success "$name is running!"
            return 0
        fi
        
        log_info "Attempt $attempt/$max_attempts: $name not ready, waiting..."
        sleep 2
        ((attempt++))
    done
    
    log_error "$name is not responding after $max_attempts attempts"
    return 1
}

# Function to run API tests
run_api_tests() {
    log_info "🧪 Running Knowledge Graph API tests..."
    
    # Check if Python is available
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is required for API tests"
        return 1
    fi
    
    # Install required packages if not available
    if ! python3 -c "import requests" 2>/dev/null; then
        log_info "Installing Python dependencies..."
        pip3 install requests
    fi
    
    # Run the API test suite
    if python3 tests/test_kg_api.py --url "$API_URL" --timeout "$TEST_TIMEOUT"; then
        log_success "✅ API tests passed!"
        return 0
    else
        log_error "❌ API tests failed!"
        return 1
    fi
}

# Function to run UI tests
run_ui_tests() {
    log_info "🎭 Running Knowledge Graph UI tests..."
    
    # Check if UI tests directory exists
    if [ ! -f "tests/test_kg_ui.spec.ts" ]; then
        log_error "UI test file not found: tests/test_kg_ui.spec.ts"
        return 1
    fi
    
    # Check if Playwright is available
    if ! command -v npx &> /dev/null; then
        log_error "Node.js/npm is required for UI tests"
        return 1
    fi
    
    # Run Playwright tests
    local playwright_args="--config=tests/config/playwright.config.ts --project=chromium"
    
    if [ "$HEADLESS" = "true" ]; then
        playwright_args="$playwright_args --headed=false"
    fi
    
    # Set environment variables for tests
    export API_BASE_URL="$API_URL"
    export UI_BASE_URL="$UI_URL"
    
    if cd tests && npx playwright test test_kg_ui.spec.ts $playwright_args; then
        log_success "✅ UI tests passed!"
        cd ..
        return 0
    else
        log_error "❌ UI tests failed!"
        cd ..
        return 1
    fi
}

# Function to run quick smoke tests
run_smoke_tests() {
    log_info "💨 Running smoke tests..."
    
    # Test basic API endpoints
    local endpoints=(
        "/api/kg/statistics"
        "/api/kg/entities?limit=1"
        "/api/kg/search?q=rama"
    )
    
    for endpoint in "${endpoints[@]}"; do
        log_info "Testing $endpoint..."
        if ! curl -s -f "${API_URL}${endpoint}" | jq -e '.success == true' > /dev/null; then
            log_error "Smoke test failed for $endpoint"
            return 1
        fi
    done
    
    log_success "✅ Smoke tests passed!"
    return 0
}

# Function to run performance tests
run_performance_tests() {
    log_info "⚡ Running performance tests..."
    
    local endpoints=(
        "/api/kg/statistics"
        "/api/kg/entities?limit=10"
        "/api/kg/search?q=rama"
    )
    
    for endpoint in "${endpoints[@]}"; do
        log_info "Performance testing $endpoint..."
        
        # Measure response time
        local start_time=$(date +%s.%N)
        if curl -s -f "${API_URL}${endpoint}" > /dev/null; then
            local end_time=$(date +%s.%N)
            local duration=$(echo "$end_time - $start_time" | bc)
            
            # Check if response time is acceptable (< 2 seconds)
            if (( $(echo "$duration < 2.0" | bc -l) )); then
                log_success "✅ $endpoint: ${duration}s"
            else
                log_warning "⚠️  $endpoint: ${duration}s (slow)"
            fi
        else
            log_error "❌ $endpoint: failed"
            return 1
        fi
    done
    
    log_success "✅ Performance tests completed!"
    return 0
}

# Function to validate data consistency
run_data_validation() {
    log_info "🔍 Running data validation tests..."
    
    # Get statistics
    local stats_response=$(curl -s "${API_URL}/api/kg/statistics")
    local total_entities=$(echo "$stats_response" | jq -r '.statistics.total_entities')
    
    # Get actual entity count
    local entities_response=$(curl -s "${API_URL}/api/kg/entities?limit=100")
    local actual_count=$(echo "$entities_response" | jq -r '.count')
    
    if [ "$total_entities" != "$actual_count" ]; then
        log_error "Data inconsistency: stats=$total_entities, actual=$actual_count"
        return 1
    fi
    
    # Validate URI format
    local invalid_uris=$(echo "$entities_response" | jq -r '.entities[].kg_id' | grep -v "ramayanam.hanuma.com" | wc -l)
    if [ "$invalid_uris" -gt 0 ]; then
        log_error "Found $invalid_uris entities with invalid URI format"
        return 1
    fi
    
    log_success "✅ Data validation passed!"
    return 0
}

# Function to generate test report
generate_report() {
    local start_time=$1
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    log_info "📊 Test Report"
    echo "========================================"
    echo "Test Duration: ${duration}s"
    echo "API URL: $API_URL"
    echo "UI URL: $UI_URL"
    echo "Timestamp: $(date)"
    echo "========================================"
}

# Function to cleanup
cleanup() {
    log_info "🧹 Cleaning up..."
    # Add any cleanup tasks here
}

# Main test runner
main() {
    local start_time=$(date +%s)
    local failed_tests=0
    
    log_info "🚀 Starting Knowledge Graph Automated Test Suite"
    log_info "=================================================="
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --api-url)
                API_URL="$2"
                shift 2
                ;;
            --ui-url)
                UI_URL="$2"
                shift 2
                ;;
            --headless)
                HEADLESS="$2"
                shift 2
                ;;
            --smoke-only)
                SMOKE_ONLY="true"
                shift
                ;;
            --skip-ui)
                SKIP_UI="true"
                shift
                ;;
            --help)
                echo "Usage: $0 [options]"
                echo "Options:"
                echo "  --api-url URL       API base URL (default: http://localhost:8080)"
                echo "  --ui-url URL        UI base URL (default: http://localhost:3000)"
                echo "  --headless BOOL     Run UI tests headless (default: true)"
                echo "  --smoke-only        Run only smoke tests"
                echo "  --skip-ui           Skip UI tests"
                echo "  --help              Show this help"
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    # Set trap for cleanup
    trap cleanup EXIT
    
    # Check if backend service is running
    if ! check_service "${API_URL}/api/kg/statistics" "Knowledge Graph API"; then
        log_error "Knowledge Graph API is not running. Please start it first."
        log_info "Try: docker-compose -f docker-compose.backend.yml up -d"
        exit 1
    fi
    
    # Run smoke tests first
    if ! run_smoke_tests; then
        ((failed_tests++))
        log_error "Smoke tests failed - aborting remaining tests"
        exit 1
    fi
    
    # If smoke-only mode, exit here
    if [ "$SMOKE_ONLY" = "true" ]; then
        log_success "🎉 Smoke tests completed successfully!"
        generate_report $start_time
        exit 0
    fi
    
    # Run API tests
    if ! run_api_tests; then
        ((failed_tests++))
    fi
    
    # Run data validation
    if ! run_data_validation; then
        ((failed_tests++))
    fi
    
    # Run performance tests
    if ! run_performance_tests; then
        ((failed_tests++))
    fi
    
    # Run UI tests (if not skipped and UI is available)
    if [ "$SKIP_UI" != "true" ]; then
        if check_service "$UI_URL" "UI Application" 2>/dev/null; then
            if ! run_ui_tests; then
                ((failed_tests++))
            fi
        else
            log_warning "UI not available at $UI_URL, skipping UI tests"
        fi
    fi
    
    # Generate final report
    echo
    log_info "🏁 Test Suite Complete"
    generate_report $start_time
    
    if [ $failed_tests -eq 0 ]; then
        log_success "🎉 All tests passed!"
        exit 0
    else
        log_error "❌ $failed_tests test suite(s) failed"
        exit 1
    fi
}

# Check dependencies
check_dependencies() {
    local missing_deps=0
    
    # Check for required tools
    local required_tools=("curl" "jq" "bc")
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            log_error "Required tool not found: $tool"
            ((missing_deps++))
        fi
    done
    
    if [ $missing_deps -gt 0 ]; then
        log_error "Please install missing dependencies before running tests"
        log_info "On macOS: brew install curl jq bc"
        log_info "On Ubuntu: sudo apt-get install curl jq bc"
        exit 1
    fi
}

# Run dependency check and main function
check_dependencies
main "$@"