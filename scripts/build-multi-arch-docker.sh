#!/bin/bash

# Build multi-architecture Docker image for Ramayanam application
# Supports linux/amd64 and linux/arm64 platforms

set -e

# Configuration
IMAGE_NAME="narenm/ramayanam"
PLATFORMS="linux/amd64,linux/arm64"
DOCKERFILE="Dockerfile"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if buildx is available
if ! docker buildx version >/dev/null 2>&1; then
    print_error "Docker buildx is not available. Please update Docker to a newer version."
    exit 1
fi

# Parse command line arguments
TAG="latest"
PUSH=false
LOAD=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--tag)
            TAG="$2"
            shift 2
            ;;
        --push)
            PUSH=true
            shift
            ;;
        --load)
            LOAD=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -t, --tag TAG     Tag for the Docker image (default: latest)"
            echo "  --push           Push the image to registry"
            echo "  --load           Load the image to local Docker (single platform only)"
            echo "  -h, --help       Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                              # Build multi-arch image with 'latest' tag"
            echo "  $0 -t v1.0.0                   # Build with custom tag"
            echo "  $0 -t v1.0.0 --push            # Build and push to registry"
            echo "  $0 --load                      # Build and load to local Docker (amd64 only)"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use -h or --help for usage information."
            exit 1
            ;;
    esac
done

# Adjust platforms if loading locally (Docker can only load single platform)
if [ "$LOAD" = true ]; then
    PLATFORMS="linux/amd64"
    print_warning "Loading to local Docker - using single platform: $PLATFORMS"
fi

# Create or use existing buildx builder
BUILDER_NAME="ramayanam-builder"
if ! docker buildx inspect "$BUILDER_NAME" >/dev/null 2>&1; then
    print_status "Creating new buildx builder: $BUILDER_NAME"
    docker buildx create --name "$BUILDER_NAME" --driver docker-container --bootstrap
else
    print_status "Using existing buildx builder: $BUILDER_NAME"
fi

# Use the builder
docker buildx use "$BUILDER_NAME"

# Build command
BUILD_CMD="docker buildx build"
BUILD_CMD="$BUILD_CMD --platform $PLATFORMS"
BUILD_CMD="$BUILD_CMD -t $IMAGE_NAME:$TAG"
BUILD_CMD="$BUILD_CMD -f $DOCKERFILE"

if [ "$PUSH" = true ]; then
    BUILD_CMD="$BUILD_CMD --push"
    print_status "Building and pushing multi-architecture image: $IMAGE_NAME:$TAG"
elif [ "$LOAD" = true ]; then
    BUILD_CMD="$BUILD_CMD --load"
    print_status "Building and loading image to local Docker: $IMAGE_NAME:$TAG"
else
    print_status "Building multi-architecture image (registry cache only): $IMAGE_NAME:$TAG"
fi

BUILD_CMD="$BUILD_CMD ."

print_status "Platforms: $PLATFORMS"
print_status "Build command: $BUILD_CMD"

# Execute the build
echo ""
eval $BUILD_CMD

# Success message
echo ""
if [ "$PUSH" = true ]; then
    print_status "✅ Multi-architecture image built and pushed successfully!"
    print_status "Image: $IMAGE_NAME:$TAG"
    print_status "Platforms: $PLATFORMS"
    echo ""
    print_status "To verify the manifest:"
    echo "  docker buildx imagetools inspect $IMAGE_NAME:$TAG"
elif [ "$LOAD" = true ]; then
    print_status "✅ Image built and loaded to local Docker successfully!"
    print_status "Image: $IMAGE_NAME:$TAG"
    echo ""
    print_status "To run locally:"
    echo "  docker run -p 5000:5000 $IMAGE_NAME:$TAG"
else
    print_status "✅ Multi-architecture image built successfully!"
    print_status "Image: $IMAGE_NAME:$TAG"
    print_status "Platforms: $PLATFORMS"
    echo ""
    print_warning "Image is stored in buildx cache only. Use --push to push to registry or --load for local use."
fi

echo ""
print_status "Available commands:"
echo "  Build and push:     $0 -t $TAG --push"
echo "  Build and load:     $0 -t $TAG --load"
echo "  Check manifest:     docker buildx imagetools inspect $IMAGE_NAME:$TAG"