#!/bin/bash

# Backend Testing Script for Ramayanam API
# Comprehensive testing suite using pytest

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
VENV_PATH="./venv"
REQUIREMENTS_FILE="requirements-test.txt"
REPORTS_DIR="reports"
COVERAGE_THRESHOLD=80

# Function to print colored output
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

print_section() {
    echo -e "${PURPLE}[SECTION]${NC} $1"
}

print_test() {
    echo -e "${CYAN}[TEST]${NC} $1"
}

# Function to check if virtual environment exists
check_venv() {
    if [ ! -d "$VENV_PATH" ]; then
        print_warning "Virtual environment not found at $VENV_PATH"
        print_status "Creating virtual environment..."
        python3 -m venv "$VENV_PATH"
        print_success "Virtual environment created"
    fi
}

# Function to activate virtual environment
activate_venv() {
    print_status "Activating virtual environment..."
    source "$VENV_PATH/bin/activate"
    print_success "Virtual environment activated"
}

# Function to install dependencies
install_dependencies() {
    print_status "Installing test dependencies..."
    
    if [ ! -f "$REQUIREMENTS_FILE" ]; then
        print_error "Requirements file $REQUIREMENTS_FILE not found"
        exit 1
    fi
    
    pip install --upgrade pip
    pip install -r "$REQUIREMENTS_FILE"
    
    print_success "Dependencies installed"
}

# Function to create reports directory
setup_reports() {
    print_status "Setting up reports directory..."
    mkdir -p "$REPORTS_DIR"
    print_success "Reports directory ready: $REPORTS_DIR"
}

# Function to run specific test suite
run_test_suite() {
    local test_type="$1"
    local test_path="$2"
    local extra_args="${3:-}"
    
    print_test "Running $test_type tests..."
    
    if [ -d "$test_path" ] || [ -f "$test_path" ]; then
        pytest "$test_path" $extra_args
        local exit_code=$?
        
        if [ $exit_code -eq 0 ]; then
            print_success "$test_type tests passed"
        else
            print_error "$test_type tests failed with exit code $exit_code"
            return $exit_code
        fi
    else
        print_warning "$test_type tests not found at $test_path"
    fi
}

# Function to run unit tests
run_unit_tests() {
    print_section "Unit Tests"
    run_test_suite "Unit" "tests/unit" "-m unit --tb=short"
}

# Function to run integration tests
run_integration_tests() {
    print_section "Integration Tests"
    run_test_suite "Integration" "tests/integration" "-m integration --tb=short"
}

# Function to run API tests
run_api_tests() {
    print_section "API Tests"
    run_test_suite "API" "tests/unit/test_api_endpoints.py" "-m api --tb=short"
}

# Function to run service tests
run_service_tests() {
    print_section "Service Tests"
    run_test_suite "Service" "tests/unit/test_services.py" "-m service --tb=short"
}

# Function to run model tests
run_model_tests() {
    print_section "Model Tests"
    run_test_suite "Model" "tests/unit/test_models.py" "-m model --tb=short"
}

# Function to run performance tests
run_performance_tests() {
    print_section "Performance Tests"
    run_test_suite "Performance" "tests/performance" "-m performance --tb=short -v"
}

# Function to run all tests with coverage
run_all_tests() {
    print_section "All Tests with Coverage"
    
    pytest tests/ \
        --cov=api \
        --cov-report=html:reports/coverage_html \
        --cov-report=xml:reports/coverage.xml \
        --cov-report=term-missing \
        --cov-fail-under=$COVERAGE_THRESHOLD \
        --html=reports/pytest_report.html \
        --self-contained-html \
        --json-report \
        --json-report-file=reports/pytest_report.json \
        --tb=short \
        -v
    
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        print_success "All tests passed with coverage >= $COVERAGE_THRESHOLD%"
    else
        print_error "Tests failed or coverage below $COVERAGE_THRESHOLD%"
        return $exit_code
    fi
}

# Function to run tests in parallel
run_parallel_tests() {
    print_section "Parallel Test Execution"
    
    pytest tests/ \
        -n auto \
        --dist=loadscope \
        --tb=short \
        -v
    
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        print_success "Parallel tests completed successfully"
    else
        print_error "Parallel tests failed"
        return $exit_code
    fi
}

# Function to lint code
run_linting() {
    print_section "Code Linting"
    
    # Check if flake8 is available
    if command -v flake8 &> /dev/null; then
        print_test "Running flake8..."
        flake8 api/ tests/ --max-line-length=120 --exclude=venv,__pycache__ || true
    else
        print_warning "flake8 not found, skipping linting"
    fi
    
    # Check if black is available
    if command -v black &> /dev/null; then
        print_test "Checking code formatting with black..."
        black --check api/ tests/ || true
    else
        print_warning "black not found, skipping format check"
    fi
}

# Function to generate test report summary
generate_summary() {
    print_section "Test Summary"
    
    if [ -f "reports/pytest_report.json" ]; then
        print_status "Test execution summary:"
        
        # Extract summary from JSON report using Python
        python3 -c "
import json
try:
    with open('reports/pytest_report.json', 'r') as f:
        data = json.load(f)
    
    summary = data.get('summary', {})
    print(f\"  Total tests: {summary.get('total', 0)}\")
    print(f\"  Passed: {summary.get('passed', 0)}\")
    print(f\"  Failed: {summary.get('failed', 0)}\")
    print(f\"  Skipped: {summary.get('skipped', 0)}\")
    print(f\"  Duration: {data.get('duration', 0):.2f} seconds\")
except Exception as e:
    print(f\"  Could not parse test report: {e}\")
"
    fi
    
    if [ -f "reports/coverage.xml" ]; then
        print_status "Coverage information available in reports/coverage.xml"
    fi
    
    if [ -f "reports/pytest_report.html" ]; then
        print_status "HTML report available at: file://$(pwd)/reports/pytest_report.html"
    fi
    
    if [ -f "reports/coverage_html/index.html" ]; then
        print_status "Coverage report available at: file://$(pwd)/reports/coverage_html/index.html"
    fi
}

# Function to clean up old reports
cleanup_reports() {
    print_status "Cleaning up old reports..."
    rm -rf "$REPORTS_DIR"/*
    print_success "Reports cleaned"
}

# Function to check test dependencies
check_dependencies() {
    print_status "Checking test dependencies..."
    
    # Check Python version
    python_version=$(python3 --version 2>&1 | awk '{print $2}')
    print_status "Python version: $python_version"
    
    # Check pytest installation
    if python3 -c "import pytest" 2>/dev/null; then
        pytest_version=$(python3 -c "import pytest; print(pytest.__version__)")
        print_status "pytest version: $pytest_version"
    else
        print_error "pytest not installed"
        return 1
    fi
    
    # Check other dependencies
    for module in flask pytest_flask pytest_cov; do
        if python3 -c "import $module" 2>/dev/null; then
            print_status "$module: ✓"
        else
            print_warning "$module: ✗ (not installed)"
        fi
    done
}

# Function to show help
show_help() {
    echo "Backend Testing Script for Ramayanam API"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  all                Run all tests with coverage (default)"
    echo "  unit               Run unit tests only"
    echo "  integration        Run integration tests only"
    echo "  api                Run API endpoint tests only"
    echo "  service            Run service layer tests only"
    echo "  model              Run model tests only"
    echo "  performance        Run performance tests only"
    echo "  parallel           Run tests in parallel"
    echo "  lint               Run code linting"
    echo "  clean              Clean reports directory"
    echo "  deps               Check dependencies"
    echo "  help               Show this help message"
    echo ""
    echo "Options:"
    echo "  --coverage-threshold N    Set coverage threshold (default: $COVERAGE_THRESHOLD)"
    echo "  --no-cleanup             Don't clean reports before running"
    echo "  --verbose                Extra verbose output"
    echo "  --quiet                  Minimal output"
    echo ""
    echo "Examples:"
    echo "  $0                       # Run all tests"
    echo "  $0 unit                  # Run only unit tests"
    echo "  $0 all --coverage-threshold 90"
    echo "  $0 parallel --verbose"
    echo ""
    echo "Environment Variables:"
    echo "  COVERAGE_THRESHOLD       Coverage threshold percentage"
    echo "  PYTEST_ARGS            Additional pytest arguments"
    echo ""
}

# Function to validate environment
validate_environment() {
    print_status "Validating test environment..."
    
    # Check if we're in the right directory
    if [ ! -f "api/app.py" ]; then
        print_error "Not in the correct directory. Please run from project root."
        exit 1
    fi
    
    # Check if tests directory exists
    if [ ! -d "tests" ]; then
        print_error "Tests directory not found"
        exit 1
    fi
    
    print_success "Environment validated"
}

# Main execution function
main() {
    local command="${1:-all}"
    local cleanup=true
    local verbose=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --coverage-threshold)
                COVERAGE_THRESHOLD="$2"
                shift 2
                ;;
            --no-cleanup)
                cleanup=false
                shift
                ;;
            --verbose)
                verbose=true
                shift
                ;;
            --quiet)
                export PYTEST_ARGS="$PYTEST_ARGS -q"
                shift
                ;;
            --help|-h|help)
                show_help
                exit 0
                ;;
            *)
                if [[ $1 != -* ]]; then
                    command="$1"
                fi
                shift
                ;;
        esac
    done
    
    # Set verbose mode
    if [ "$verbose" = true ]; then
        export PYTEST_ARGS="$PYTEST_ARGS -v -s"
    fi
    
    echo "🧪 Backend Testing Suite for Ramayanam API"
    echo "==========================================="
    
    # Validate environment
    validate_environment
    
    # Setup
    check_venv
    activate_venv
    install_dependencies
    setup_reports
    
    # Clean reports if requested
    if [ "$cleanup" = true ] && [ "$command" != "clean" ]; then
        cleanup_reports
    fi
    
    # Execute command
    case $command in
        all)
            run_all_tests
            ;;
        unit)
            run_unit_tests
            ;;
        integration)
            run_integration_tests
            ;;
        api)
            run_api_tests
            ;;
        service)
            run_service_tests
            ;;
        model)
            run_model_tests
            ;;
        performance)
            run_performance_tests
            ;;
        parallel)
            run_parallel_tests
            ;;
        lint)
            run_linting
            ;;
        clean)
            cleanup_reports
            ;;
        deps)
            check_dependencies
            ;;
        *)
            print_error "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
    
    local exit_code=$?
    
    # Generate summary for test commands
    if [[ "$command" =~ ^(all|unit|integration|api|service|model|performance|parallel)$ ]]; then
        generate_summary
    fi
    
    echo ""
    echo "==========================================="
    if [ $exit_code -eq 0 ]; then
        print_success "🎉 Testing completed successfully!"
    else
        print_error "❌ Testing failed"
    fi
    echo "==========================================="
    
    exit $exit_code
}

# Run main function with all arguments
main "$@"