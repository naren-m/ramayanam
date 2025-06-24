#!/bin/bash

# Multi-architecture Docker image build and push script
# Builds ARM64 on multipass VM and AMD64 on cluster node, then pushes both

set -e

# Configuration
DOCKER_REPO="narenm/ramayanam"
ARM64_VM="k3s-worker-mac"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "🚀 Starting multi-architecture build for $DOCKER_REPO"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check dependencies
if ! command_exists multipass; then
    echo "❌ Error: multipass is required but not installed"
    exit 1
fi

if ! command_exists kubectl; then
    echo "❌ Error: kubectl is required but not installed"
    exit 1
fi

if ! command_exists docker; then
    echo "❌ Error: docker is required but not installed"
    exit 1
fi

echo "📋 Building images for both architectures..."

# Build ARM64 image on multipass VM
echo "🔧 Building ARM64 image on VM: $ARM64_VM"

# Clean up existing project on VM
echo "🧹 Cleaning up existing files on VM..."
multipass exec "$ARM64_VM" -- sudo rm -rf /home/ubuntu/ramayanam || true

echo "📦 Transferring project files to VM (excluding .git)..."
# Use rsync to exclude .git and other problematic directories
rsync -av --exclude='.git' --exclude='node_modules' --exclude='dist' --exclude='__pycache__' --exclude='venv' \
    -e "multipass exec $ARM64_VM -- bash -c 'cat > /tmp/rsync_wrapper && chmod +x /tmp/rsync_wrapper'" \
    "$PROJECT_DIR/" "/tmp/ramayanam_sync/"

# Alternative: Use tar to transfer files
echo "📦 Creating project archive..."
cd "$PROJECT_DIR"
tar --exclude='.git' --exclude='node_modules' --exclude='dist' --exclude='__pycache__' --exclude='venv' \
    -czf /tmp/ramayanam.tar.gz .

echo "📤 Transferring archive to VM..."
multipass transfer /tmp/ramayanam.tar.gz "$ARM64_VM:/tmp/ramayanam.tar.gz"

echo "📂 Extracting project on VM..."
multipass exec "$ARM64_VM" -- bash -c "
    mkdir -p /home/ubuntu/ramayanam &&
    cd /home/ubuntu/ramayanam &&
    tar -xzf /tmp/ramayanam.tar.gz &&
    rm /tmp/ramayanam.tar.gz
"

echo "🏗️  Building ARM64 Docker image..."
multipass exec "$ARM64_VM" -- bash -c "
    cd /home/ubuntu/ramayanam && 
    sudo docker build -t $DOCKER_REPO:arm64 .
"

if [ $? -eq 0 ]; then
    echo "✅ ARM64 image built successfully"
else
    echo "❌ ARM64 image build failed"
    exit 1
fi

# Build AMD64 image on cluster node
echo "🏗️  Building AMD64 Docker image on cluster node..."

# Find an AMD64 node - prefer hanuma if available
AMD64_NODES=$(kubectl get nodes -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.nodeInfo.architecture}{"\n"}{end}' | grep amd64 | cut -f1)

# Try to use hanuma first, otherwise use the first available AMD64 node
if echo "$AMD64_NODES" | grep -q "hanuma"; then
    AMD64_NODE="hanuma"
else
    AMD64_NODE=$(echo "$AMD64_NODES" | head -1)
fi

AMD64_NODE_IP=$(kubectl get node "$AMD64_NODE" -o jsonpath='{.status.addresses[?(@.type=="InternalIP")].address}')

echo "🎯 Using AMD64 node: $AMD64_NODE ($AMD64_NODE_IP)"

# Determine username based on node name
if [[ "$AMD64_NODE" == *"hanuma"* ]]; then
    AMD64_USER="narenuday"
    # Override IP for hanuma if needed
    AMD64_NODE_IP="192.168.68.124"
elif [[ "$AMD64_NODE" == *"dell-mini"* ]]; then
    AMD64_USER="narenmudivarthy"
else
    AMD64_USER="ubuntu"
fi

echo "👤 Using username: $AMD64_USER for node $AMD64_NODE"

# Clean up existing project on AMD64 node
echo "🧹 Cleaning up existing files on AMD64 node..."
ssh -o StrictHostKeyChecking=no -o PasswordAuthentication=no "$AMD64_USER@$AMD64_NODE_IP" "sudo rm -rf /tmp/ramayanam*" || true

# Transfer project to AMD64 node using tar
echo "📦 Transferring project files to AMD64 node..."
scp -o StrictHostKeyChecking=no -o PasswordAuthentication=no /tmp/ramayanam.tar.gz "$AMD64_USER@$AMD64_NODE_IP:/tmp/ramayanam.tar.gz"

echo "📂 Extracting project on AMD64 node..."
ssh -o StrictHostKeyChecking=no -o PasswordAuthentication=no "$AMD64_USER@$AMD64_NODE_IP" "
    rm -rf /tmp/ramayanam &&
    mkdir -p /tmp/ramayanam &&
    cd /tmp/ramayanam &&
    tar -xzf /tmp/ramayanam.tar.gz &&
    ls -la &&
    echo 'Files extracted:' &&
    find . -name 'Dockerfile' -type f &&
    rm /tmp/ramayanam.tar.gz
"

# Build AMD64 image on the node
echo "🏗️  Building AMD64 Docker image on node..."
ssh -o StrictHostKeyChecking=no -o PasswordAuthentication=no "$AMD64_USER@$AMD64_NODE_IP" "
    cd /tmp/ramayanam && 
    pwd &&
    ls -la &&
    echo 'Current directory contents before build:' &&
    cat Dockerfile | head -5 &&
    sudo docker build -t $DOCKER_REPO:amd64 .
"

if [ $? -eq 0 ]; then
    echo "✅ AMD64 image built successfully"
else
    echo "❌ AMD64 image build failed"
    exit 1
fi

# Clean up local tar file
rm -f /tmp/ramayanam.tar.gz

# Push images
echo "📤 Pushing images to Docker Hub..."

# Login check
if ! docker info | grep -q "Username:"; then
    echo "🔐 Please login to Docker Hub first:"
    docker login
fi

# Check Docker login on VM
echo "🔐 Checking Docker Hub login on VM..."
if ! multipass exec "$ARM64_VM" -- sudo docker info | grep -q "Username:"; then
    echo "❌ Error: Not logged in to Docker Hub on VM"
    echo "💡 Please run: multipass exec $ARM64_VM -- sudo docker login --username narenm"
    exit 1
fi

# Check Docker login on AMD64 node
echo "🔐 Checking Docker Hub login on AMD64 node..."
if ! ssh -o StrictHostKeyChecking=no "$AMD64_USER@$AMD64_NODE_IP" "sudo docker info | grep -q Username"; then
    echo "❌ Error: Not logged in to Docker Hub on AMD64 node"
    echo "💡 Please run: ssh $AMD64_USER@$AMD64_NODE_IP 'sudo docker login --username narenm'"
    exit 1
fi

# Push ARM64 image from VM
echo "📤 Pushing ARM64 image..."
multipass exec "$ARM64_VM" -- bash -c "
    echo 'Pushing ARM64 image from VM...' &&
    sudo docker push $DOCKER_REPO:arm64
"

if [ $? -eq 0 ]; then
    echo "✅ ARM64 image pushed successfully"
else
    echo "❌ ARM64 image push failed"
    exit 1
fi

# Push AMD64 image from the node
echo "📤 Pushing AMD64 image from node..."
ssh -o StrictHostKeyChecking=no "$AMD64_USER@$AMD64_NODE_IP" "
    sudo docker push $DOCKER_REPO:amd64
"

if [ $? -eq 0 ]; then
    echo "✅ AMD64 image pushed successfully"
else
    echo "❌ AMD64 image push failed"
    exit 1
fi

# Create and push multi-arch manifest
echo "🏷️  Creating multi-arch manifest..."

# Create manifest for both architectures
docker manifest create "$DOCKER_REPO:latest" \
    "$DOCKER_REPO:amd64" \
    "$DOCKER_REPO:arm64"

docker manifest annotate "$DOCKER_REPO:latest" "$DOCKER_REPO:amd64" --arch amd64
docker manifest annotate "$DOCKER_REPO:latest" "$DOCKER_REPO:arm64" --arch arm64

echo "📤 Pushing multi-arch manifest..."
docker manifest push "$DOCKER_REPO:latest"

if [ $? -eq 0 ]; then
    echo "✅ Multi-arch manifest pushed successfully"
else
    echo "⚠️  Multi-arch manifest push failed (but individual images are available)"
fi

# Clean up on nodes
echo "🧹 Cleaning up temporary files..."
multipass exec "$ARM64_VM" -- sudo rm -rf /home/ubuntu/ramayanam || true
ssh -o StrictHostKeyChecking=no "$AMD64_USER@$AMD64_NODE_IP" "sudo rm -rf /tmp/ramayanam" || true

echo ""
echo "🎉 Multi-architecture build and push completed successfully!"
echo ""
echo "📋 Available images:"
echo "   • $DOCKER_REPO:arm64 (for ARM64 nodes)"
echo "   • $DOCKER_REPO:amd64 (for AMD64 nodes)"
echo "   • $DOCKER_REPO:latest (multi-arch manifest)"
echo ""
echo "🚀 You can now deploy using:"
echo "   kubectl apply -f k8s/deployment-arm64.yaml"
echo "   kubectl apply -f k8s/deployment-amd64.yaml"
echo ""
echo "🔧 Or use the latest tag with automatic architecture selection:"
echo "   kubectl set image deployment/ramayanam-app-amd64 ramayanam=$DOCKER_REPO:latest -n ramayanam"
echo "   kubectl set image deployment/ramayanam-app-arm64 ramayanam=$DOCKER_REPO:latest -n ramayanam"
