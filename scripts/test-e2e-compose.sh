#!/bin/bash

# E2E Test Script using Docker Compose
# This script uses docker-compose to run the app and tests in isolated containers

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Function to cleanup
cleanup() {
    print_status "Cleaning up..."
    docker-compose -f docker-compose.test.yml down --volumes --remove-orphans >/dev/null 2>&1 || true
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    
    if [ ! -f "docker-compose.test.yml" ]; then
        print_error "docker-compose.test.yml not found. Please run this script from the project root."
        exit 1
    fi
    
    print_success "All prerequisites are met"
}

# Function to build and run tests
run_tests() {
    print_status "Building and starting services..."
    
    # Build the images
    if ! docker-compose -f docker-compose.test.yml build; then
        print_error "Failed to build Docker images"
        exit 1
    fi
    
    print_status "Starting application service..."
    
    # Start the app service and wait for it to be healthy
    if ! docker-compose -f docker-compose.test.yml up -d app; then
        print_error "Failed to start application service"
        exit 1
    fi
    
    print_status "Waiting for application to be healthy..."
    
    # Wait for the app to be healthy
    local counter=0
    local max_attempts=60  # 10 minutes
    
    while [ $counter -lt $max_attempts ]; do
        if docker-compose -f docker-compose.test.yml ps app | grep -q "healthy"; then
            print_success "Application is healthy!"
            break
        fi
        
        counter=$((counter + 1))
        echo -n "."
        sleep 10
        
        if [ $counter -eq $max_attempts ]; then
            print_error "Application failed to become healthy"
            show_app_logs
            exit 1
        fi
    done
    
    print_status "Running E2E tests..."
    
    # Run the E2E tests
    if docker-compose -f docker-compose.test.yml run --rm e2e-tests; then
        print_success "E2E tests completed successfully!"
        return 0
    else
        print_warning "Some E2E tests failed"
        return 1
    fi
}

# Function to show application logs
show_app_logs() {
    print_status "Application logs:"
    echo "----------------------------------------"
    docker-compose -f docker-compose.test.yml logs app
    echo "----------------------------------------"
}

# Function to show test logs
show_test_logs() {
    print_status "Test logs:"
    echo "----------------------------------------"
    docker-compose -f docker-compose.test.yml logs e2e-tests
    echo "----------------------------------------"
}

# Trap to ensure cleanup on exit
trap cleanup EXIT

# Main execution
main() {
    echo "🚀 Starting E2E Test Suite with Docker Compose"
    echo "==============================================="
    
    # Check prerequisites
    check_prerequisites
    
    # Cleanup any existing resources
    cleanup
    
    # Run tests
    if run_tests; then
        print_success "🎉 E2E test suite completed successfully!"
        TEST_RESULT=0
    else
        print_warning "⚠️  Some tests failed"
        show_app_logs
        show_test_logs
        TEST_RESULT=1
    fi
    
    echo ""
    echo "==============================================="
    echo "🏁 E2E Test Suite Complete"
    echo "==============================================="
    
    return $TEST_RESULT
}

# Parse command line arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --help, -h        Show this help message"
        echo "  --no-cleanup      Don't cleanup Docker resources after tests"
        echo "  --build-only      Only build the Docker images"
        echo "  --logs            Show application and test logs"
        echo "  --app-logs        Show only application logs"
        echo "  --test-logs       Show only test logs"
        echo ""
        exit 0
        ;;
    --no-cleanup)
        trap - EXIT
        main
        ;;
    --build-only)
        check_prerequisites
        print_status "Building Docker images..."
        docker-compose -f docker-compose.test.yml build
        print_success "Docker images built successfully"
        exit 0
        ;;
    --logs)
        show_app_logs
        show_test_logs
        exit 0
        ;;
    --app-logs)
        show_app_logs
        exit 0
        ;;
    --test-logs)
        show_test_logs
        exit 0
        ;;
    "")
        main
        ;;
    *)
        print_error "Unknown option: $1"
        echo "Use --help for usage information"
        exit 1
        ;;
esac