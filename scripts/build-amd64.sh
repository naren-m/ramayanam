#!/bin/bash

# AMD64 Docker image build and push script
# Builds AMD64 image on cluster node and pushes to Docker Hub

set -e

# Configuration
DOCKER_REPO="narenm/ramayanam"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "🚀 Starting AMD64 build for $DOCKER_REPO"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check dependencies
if ! command_exists kubectl; then
    echo "❌ Error: kubectl is required but not installed"
    exit 1
fi

if ! command_exists docker; then
    echo "❌ Error: docker is required but not installed"
    exit 1
fi

# Find an AMD64 node
echo "🔍 Finding AMD64 cluster node..."
AMD64_NODE=$(kubectl get nodes -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.nodeInfo.architecture}{"\n"}{end}' | grep amd64 | head -1 | cut -f1)

if [ -z "$AMD64_NODE" ]; then
    echo "❌ Error: No AMD64 nodes found in cluster"
    exit 1
fi

AMD64_NODE_IP=$(kubectl get node "$AMD64_NODE" -o jsonpath='{.status.addresses[?(@.type=="InternalIP")].address}')

echo "🎯 Using AMD64 node: $AMD64_NODE ($AMD64_NODE_IP)"

# Clean up any existing project on the node
echo "🧹 Cleaning up existing files on node..."
ssh -o StrictHostKeyChecking=no "ubuntu@$AMD64_NODE_IP" "sudo rm -rf /tmp/ramayanam" || true

# Transfer project to AMD64 node (excluding .git to avoid permission issues)
echo "📦 Transferring project files to AMD64 node..."
rsync -av --exclude='.git' --exclude='node_modules' --exclude='dist' --exclude='__pycache__' --exclude='venv' \
    "$PROJECT_DIR/" "ubuntu@$AMD64_NODE_IP:/tmp/ramayanam/"

# Build AMD64 image on the node
echo "🏗️  Building AMD64 Docker image on node..."
ssh -o StrictHostKeyChecking=no "ubuntu@$AMD64_NODE_IP" "
    cd /tmp/ramayanam && 
    sudo docker build -t $DOCKER_REPO:amd64 .
"

if [ $? -eq 0 ]; then
    echo "✅ AMD64 image built successfully"
else
    echo "❌ AMD64 image build failed"
    exit 1
fi

# Check if logged in to Docker Hub
echo "🔐 Checking Docker Hub login on node..."
ssh -o StrictHostKeyChecking=no "ubuntu@$AMD64_NODE_IP" "sudo docker info | grep -q Username" || {
    echo "❌ Error: Not logged in to Docker Hub on the node"
    echo "💡 Please run the following command to login on the node:"
    echo "   ssh ubuntu@$AMD64_NODE_IP"
    echo "   sudo docker login --username narenm"
    exit 1
}

# Push AMD64 image from the node
echo "📤 Pushing AMD64 image from node..."
ssh -o StrictHostKeyChecking=no "ubuntu@$AMD64_NODE_IP" "
    sudo docker push $DOCKER_REPO:amd64
"

if [ $? -eq 0 ]; then
    echo "✅ AMD64 image pushed successfully"
else
    echo "❌ AMD64 image push failed"
    exit 1
fi

# Clean up
echo "🧹 Cleaning up files on node..."
ssh -o StrictHostKeyChecking=no "ubuntu@$AMD64_NODE_IP" "sudo rm -rf /tmp/ramayanam"

echo ""
echo "🎉 AMD64 build and push completed successfully!"
echo ""
echo "📋 Available image:"
echo "   • $DOCKER_REPO:amd64 (for AMD64 nodes)"
echo ""
echo "🚀 You can now deploy using:"
echo "   kubectl apply -f k8s/deployment-amd64.yaml"
echo ""
echo "🔧 Or update existing deployment:"
echo "   kubectl set image deployment/ramayanam-app-amd64 ramayanam=$DOCKER_REPO:amd64 -n ramayanam"