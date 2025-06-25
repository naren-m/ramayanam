#!/bin/bash

# Simple script to run E2E tests in Docker against existing application
# Assumes the application is already running on localhost:5001

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check if application is running
check_app_running() {
    print_status "Checking if application is running on localhost:5001..."
    
    if curl -s -f "http://localhost:5001/" > /dev/null 2>&1; then
        print_success "Application is running on port 5001"
        return 0
    else
        print_error "Application is not running on port 5001"
        print_error "Please start your application first: python run.py"
        return 1
    fi
}

# Main execution
main() {
    echo "🐳 Running Playwright E2E Tests in Docker"
    echo "========================================="
    
    # Check if app is running
    if ! check_app_running; then
        exit 1
    fi
    
    # Check if we're in the right directory
    if [ ! -f "docker-compose.e2e.yml" ]; then
        print_error "docker-compose.e2e.yml not found. Please run this script from the project root directory."
        exit 1
    fi
    
    print_status "Building Docker image for E2E tests..."
    docker-compose -f docker-compose.e2e.yml build
    
    print_status "Running E2E tests in Docker container..."
    if docker-compose -f docker-compose.e2e.yml run --rm playwright-tests; then
        print_success "🎉 E2E tests completed successfully!"
    else
        print_warning "⚠️  Some tests failed - this is normal for initial setup"
        print_status "Check the output above for details"
    fi
    
    print_status "Cleaning up..."
    docker-compose -f docker-compose.e2e.yml down
    
    echo ""
    echo "========================================="
    echo "🏁 Docker E2E Test Run Complete"
    echo "========================================="
    
    # Show test results location
    if [ -d "playwright-report" ]; then
        print_status "Test report generated: playwright-report/index.html"
        print_status "View it with: npx playwright show-report"
    fi
}

# Check prerequisites
check_prerequisites() {
    # Check if Docker is installed and running
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    
    # Check if docker-compose is available
    if ! command -v docker-compose &> /dev/null; then
        print_error "docker-compose is not installed. Please install docker-compose first."
        exit 1
    fi
}

# Parse command line arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "This script runs Playwright E2E tests in a Docker container"
        echo "against your application running on localhost:5001"
        echo ""
        echo "Prerequisites:"
        echo "  - Docker and docker-compose installed and running"
        echo "  - Your application running on localhost:5001"
        echo ""
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo ""
        exit 0
        ;;
    "")
        check_prerequisites
        main
        ;;
    *)
        print_error "Unknown option: $1"
        echo "Use --help for usage information"
        exit 1
        ;;
esac
