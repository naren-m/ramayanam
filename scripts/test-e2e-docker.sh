#!/bin/bash

# E2E Test Script with Docker
# This script builds and runs the Docker container, then executes E2E tests against it

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOCKER_IMAGE_NAME="ramayanam"
DOCKER_CONTAINER_NAME="ramayanam-e2e-test"
APP_PORT=5000
TEST_TIMEOUT=300  # 5 minutes timeout for app startup

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

# Function to cleanup Docker resources
cleanup_docker() {
    print_status "Cleaning up Docker resources..."
    
    # Stop and remove container if it exists
    if docker ps -a --format "table {{.Names}}" | grep -q "^${DOCKER_CONTAINER_NAME}$"; then
        print_status "Stopping and removing existing container: ${DOCKER_CONTAINER_NAME}"
        docker stop ${DOCKER_CONTAINER_NAME} >/dev/null 2>&1 || true
        docker rm ${DOCKER_CONTAINER_NAME} >/dev/null 2>&1 || true
    fi
}

# Function to wait for application to be ready
wait_for_app() {
    print_status "Waiting for application to be ready on port ${APP_PORT}..."
    
    local counter=0
    local max_attempts=$((TEST_TIMEOUT / 5))
    
    while [ $counter -lt $max_attempts ]; do
        if curl -s -f "http://localhost:${APP_PORT}/" >/dev/null 2>&1; then
            print_success "Application is ready!"
            return 0
        fi
        
        counter=$((counter + 1))
        echo -n "."
        sleep 5
    done
    
    print_error "Application failed to start within ${TEST_TIMEOUT} seconds"
    return 1
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if Docker is installed and running
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    
    # Check if Node.js is installed for Playwright
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js first."
        exit 1
    fi
    
    # Check if npm is installed
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed. Please install npm first."
        exit 1
    fi
    
    print_success "All prerequisites are met"
}

# Function to build Docker image
build_docker_image() {
    print_status "Building Docker image: ${DOCKER_IMAGE_NAME}"
    
    # Check if we're in the right directory
    if [ ! -f "Dockerfile" ]; then
        print_error "Dockerfile not found. Please run this script from the project root directory."
        exit 1
    fi
    
    # Build the Docker image
    if docker build -t ${DOCKER_IMAGE_NAME} .; then
        print_success "Docker image built successfully"
    else
        print_error "Failed to build Docker image"
        exit 1
    fi
}

# Function to run Docker container
run_docker_container() {
    print_status "Starting Docker container: ${DOCKER_CONTAINER_NAME}"
    
    # Run the container in detached mode
    if docker run -d \
        --name ${DOCKER_CONTAINER_NAME} \
        -p ${APP_PORT}:5000 \
        -e FLASK_ENV=production \
        ${DOCKER_IMAGE_NAME}; then
        print_success "Docker container started successfully"
    else
        print_error "Failed to start Docker container"
        exit 1
    fi
    
    # Show container logs for debugging
    print_status "Container logs (first 20 lines):"
    docker logs ${DOCKER_CONTAINER_NAME} 2>&1 | head -20
}

# Function to install test dependencies
install_test_dependencies() {
    print_status "Installing test dependencies..."
    
    # Install root package dependencies (Playwright)
    if [ -f "package.json" ]; then
        npm install
    fi
    
    # Install Playwright browsers if needed
    if ! npx playwright --version >/dev/null 2>&1; then
        print_status "Installing Playwright browsers..."
        npx playwright install
    fi
    
    print_success "Test dependencies installed"
}

# Function to run E2E tests
run_e2e_tests() {
    print_status "Running E2E tests..."
    
    # Update Playwright config to use the correct base URL
    if [ -f "playwright.config.ts" ]; then
        # Temporarily update the config for Docker testing
        sed -i.bak "s|command: 'python run.py'|command: 'echo \"Using Docker container\"'|g" playwright.config.ts
        sed -i.bak "s|reuseExistingServer: !process.env.CI|reuseExistingServer: true|g" playwright.config.ts
    fi
    
    # Run the tests
    if npx playwright test --reporter=line; then
        print_success "E2E tests completed"
        TEST_RESULT=0
    else
        print_warning "Some E2E tests failed (this is expected for first run)"
        TEST_RESULT=1
    fi
    
    # Restore original config
    if [ -f "playwright.config.ts.bak" ]; then
        mv playwright.config.ts.bak playwright.config.ts
    fi
    
    return $TEST_RESULT
}

# Function to generate test report
generate_test_report() {
    print_status "Generating test report..."
    
    if npx playwright show-report --host=0.0.0.0 --port=9323 &>/dev/null &
        PID=$!
        print_success "Test report available at: http://localhost:9323"
        print_status "Report server PID: $PID (kill with: kill $PID)"
    fi
}

# Function to show container logs
show_container_logs() {
    print_status "Container logs:"
    echo "----------------------------------------"
    docker logs ${DOCKER_CONTAINER_NAME} 2>&1 | tail -50
    echo "----------------------------------------"
}

# Trap to ensure cleanup on exit
trap cleanup_docker EXIT

# Main execution
main() {
    echo "🚀 Starting E2E Test Suite with Docker"
    echo "========================================"
    
    # Check prerequisites
    check_prerequisites
    
    # Cleanup any existing resources
    cleanup_docker
    
    # Build Docker image
    build_docker_image
    
    # Install test dependencies
    install_test_dependencies
    
    # Run Docker container
    run_docker_container
    
    # Wait for application to be ready
    if wait_for_app; then
        # Run E2E tests
        if run_e2e_tests; then
            print_success "🎉 All E2E tests passed!"
        else
            print_warning "⚠️  Some tests failed - check the output above"
            show_container_logs
        fi
        
        # Generate test report
        generate_test_report
        
    else
        print_error "Application failed to start - showing container logs:"
        show_container_logs
        exit 1
    fi
    
    echo ""
    echo "========================================"
    echo "🏁 E2E Test Suite Complete"
    echo "========================================"
}

# Parse command line arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --no-cleanup   Don't cleanup Docker resources after tests"
        echo "  --build-only   Only build the Docker image"
        echo "  --logs         Show container logs and exit"
        echo ""
        echo "Environment Variables:"
        echo "  APP_PORT       Port to run the application (default: 5000)"
        echo "  TEST_TIMEOUT   Timeout for app startup in seconds (default: 300)"
        echo ""
        exit 0
        ;;
    --no-cleanup)
        trap - EXIT
        main
        ;;
    --build-only)
        check_prerequisites
        build_docker_image
        print_success "Docker image built. Run without --build-only to run tests."
        exit 0
        ;;
    --logs)
        if docker ps --format "table {{.Names}}" | grep -q "^${DOCKER_CONTAINER_NAME}$"; then
            show_container_logs
        else
            print_error "Container ${DOCKER_CONTAINER_NAME} is not running"
            exit 1
        fi
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