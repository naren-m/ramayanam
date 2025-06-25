#!/bin/bash

# Master Test Runner Script
# Supports all 3 test categories: Unit, End-to-End, UI
# Can run individually or all together

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPORTS_DIR="$SCRIPT_DIR/reports"
COMPOSE_FILE="$SCRIPT_DIR/docker-compose.tests.yml"

# Create reports directory
mkdir -p "$REPORTS_DIR"

# Helper functions
print_header() {
    echo -e "\n${BLUE}================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Clean up function
cleanup() {
    print_info "Cleaning up..."
    docker-compose -f "$COMPOSE_FILE" down --volumes --remove-orphans >/dev/null 2>&1 || true
}

# Trap cleanup on exit
trap cleanup EXIT

# Show usage
usage() {
    cat << EOF
Usage: $0 [OPTION]

Test Categories:
  unit        Run unit tests only (fastest, no dependencies)
  e2e         Run end-to-end API tests only  
  ui          Run UI tests only
  performance Run performance tests only
  all         Run all test categories (default)

Options:
  --build     Force rebuild of test containers
  --reports   Start report server after tests
  --help      Show this help message

Examples:
  $0                    # Run all tests
  $0 unit              # Run unit tests only
  $0 e2e --build       # Run E2E tests with container rebuild
  $0 all --reports     # Run all tests and start report server

EOF
}

# Parse arguments
TEST_CATEGORY="all"
FORCE_BUILD=""
START_REPORTS=""

while [[ $# -gt 0 ]]; do
    case $1 in
        unit|e2e|ui|performance|all)
            TEST_CATEGORY="$1"
            shift
            ;;
        --build)
            FORCE_BUILD="--build"
            shift
            ;;
        --reports)
            START_REPORTS="true"
            shift
            ;;
        --help)
            usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Main execution
main() {
    print_header "Ramayanam Test Suite Runner"
    
    check_docker
    
    print_info "Test Category: $TEST_CATEGORY"
    print_info "Reports Directory: $REPORTS_DIR"
    
    # Start timing
    START_TIME=$(date +%s)
    
    case $TEST_CATEGORY in
        "unit")
            print_header "Running Unit Tests"
            docker-compose -f "$COMPOSE_FILE" run --rm $FORCE_BUILD unit-tests
            ;;
        "e2e")
            print_header "Running End-to-End API Tests"
            docker-compose -f "$COMPOSE_FILE" up -d $FORCE_BUILD app
            docker-compose -f "$COMPOSE_FILE" run --rm e2e-tests
            ;;
        "ui")
            print_header "Running UI Tests"
            docker-compose -f "$COMPOSE_FILE" up -d $FORCE_BUILD app
            docker-compose -f "$COMPOSE_FILE" run --rm ui-tests
            ;;
        "performance")
            print_header "Running Performance Tests"
            docker-compose -f "$COMPOSE_FILE" up -d $FORCE_BUILD app
            docker-compose -f "$COMPOSE_FILE" run --rm performance-tests
            ;;
        "all")
            print_header "Running All Test Categories"
            docker-compose -f "$COMPOSE_FILE" up -d $FORCE_BUILD app
            docker-compose -f "$COMPOSE_FILE" run --rm test-runner
            ;;
    esac
    
    # Calculate execution time
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    
    print_success "Tests completed in ${DURATION} seconds"
    
    # Start report server if requested
    if [[ "$START_REPORTS" == "true" ]]; then
        print_header "Starting Test Report Server"
        print_info "Reports will be available at: http://localhost:8080"
        print_info "Press Ctrl+C to stop the report server"
        docker-compose -f "$COMPOSE_FILE" up report-server
    fi
    
    print_success "Test execution completed successfully!"
}

# Run main function
main