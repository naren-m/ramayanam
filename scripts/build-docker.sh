#!/bin/bash

# Build Docker image for Ramayanam application
set -e

echo "Building Ramayanam Docker image..."
docker build -t ramayanam:latest .

echo "Build completed successfully!"
echo ""
echo "To run locally:"
echo "  docker run -p 5000:5000 ramayanam:latest"
echo ""
echo "To run with docker-compose:"
echo "  docker-compose up"