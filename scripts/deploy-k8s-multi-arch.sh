#!/bin/bash

# Deploy Ramayanam application to Kubernetes cluster with multi-architecture support
# This script handles namespace creation, deployment, services, and configuration

set -e

# Configuration
NAMESPACE="ramayanam"
APP_NAME="ramayanam"
IMAGE_NAME="narenm/ramayanam:latest"
K8S_DIR="k8s"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

print_header() {
    echo -e "${BLUE}[DEPLOY]${NC} $1"
}

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed or not in PATH"
    exit 1
fi

# Check if kubectl can connect to cluster
if ! kubectl cluster-info &> /dev/null; then
    print_error "Cannot connect to Kubernetes cluster. Please check your kubeconfig."
    exit 1
fi

# Get cluster info
CLUSTER_NAME=$(kubectl config current-context)
print_status "Connected to cluster: $CLUSTER_NAME"

# Check available nodes and architectures
print_header "Checking cluster architecture support"
echo "Available nodes and architectures:"
kubectl get nodes -o wide --show-labels | grep -E "NAME|kubernetes.io/arch" || kubectl get nodes -o custom-columns=NAME:.metadata.name,ARCH:.metadata.labels."kubernetes\.io/arch",OS:.metadata.labels."kubernetes\.io/os"

# Parse command line arguments
FORCE_DEPLOY=false
DRY_RUN=false
WAIT_FOR_READY=true

while [[ $# -gt 0 ]]; do
    case $1 in
        --force)
            FORCE_DEPLOY=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --no-wait)
            WAIT_FOR_READY=false
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --force      Force deployment even if resources exist"
            echo "  --dry-run    Show what would be deployed without applying"
            echo "  --no-wait    Don't wait for pods to be ready"
            echo "  -h, --help   Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                    # Deploy with default settings"
            echo "  $0 --force           # Force redeploy existing resources"
            echo "  $0 --dry-run         # Preview deployment"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use -h or --help for usage information."
            exit 1
            ;;
    esac
done

# Check if K8s directory exists
if [ ! -d "$K8S_DIR" ]; then
    print_error "Kubernetes manifests directory '$K8S_DIR' not found"
    exit 1
fi

# Function to apply manifest with error handling
apply_manifest() {
    local file="$1"
    local description="$2"
    
    if [ ! -f "$file" ]; then
        print_error "Manifest file not found: $file"
        return 1
    fi
    
    print_status "Applying $description..."
    
    if [ "$DRY_RUN" = true ]; then
        echo "DRY RUN - Would apply: $file"
        kubectl apply -f "$file" --dry-run=client
    else
        if [ "$FORCE_DEPLOY" = true ]; then
            kubectl apply -f "$file" --force
        else
            kubectl apply -f "$file"
        fi
    fi
}

# Function to wait for deployment
wait_for_deployment() {
    if [ "$WAIT_FOR_READY" = false ] || [ "$DRY_RUN" = true ]; then
        return 0
    fi
    
    print_status "Waiting for deployment to be ready..."
    if kubectl wait --for=condition=Available deployment/$APP_NAME -n $NAMESPACE --timeout=300s; then
        print_status "✅ Deployment is ready!"
    else
        print_error "❌ Deployment failed to become ready within timeout"
        return 1
    fi
}

# Function to show deployment status
show_status() {
    if [ "$DRY_RUN" = true ]; then
        return 0
    fi
    
    print_header "Current Deployment Status"
    
    echo ""
    print_status "Namespace:"
    kubectl get namespace $NAMESPACE -o wide 2>/dev/null || echo "Namespace not found"
    
    echo ""
    print_status "Pods:"
    kubectl get pods -n $NAMESPACE -o wide
    
    echo ""
    print_status "Services:"
    kubectl get services -n $NAMESPACE -o wide
    
    echo ""
    print_status "Deployment:"
    kubectl get deployment -n $NAMESPACE -o wide
    
    echo ""
    print_status "ConfigMap:"
    kubectl get configmap -n $NAMESPACE
    
    echo ""
    print_status "Ingress:"
    kubectl get ingress -n $NAMESPACE -o wide 2>/dev/null || echo "No ingress found"
}

# Function to get access information
show_access_info() {
    if [ "$DRY_RUN" = true ]; then
        return 0
    fi
    
    print_header "Access Information"
    
    # NodePort access
    NODEPORT=$(kubectl get service ${APP_NAME}-nodeport -n $NAMESPACE -o jsonpath='{.spec.ports[0].nodePort}' 2>/dev/null || echo "")
    if [ -n "$NODEPORT" ]; then
        NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="ExternalIP")].address}' 2>/dev/null)
        if [ -z "$NODE_IP" ]; then
            NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}' 2>/dev/null)
        fi
        
        if [ -n "$NODE_IP" ]; then
            print_status "🌐 NodePort Access: http://$NODE_IP:$NODEPORT"
        else
            print_status "🌐 NodePort: $NODEPORT (use any node IP)"
        fi
    fi
    
    # Ingress access
    INGRESS_HOST=$(kubectl get ingress ${APP_NAME}-ingress -n $NAMESPACE -o jsonpath='{.spec.rules[0].host}' 2>/dev/null || echo "")
    if [ -n "$INGRESS_HOST" ]; then
        print_status "🌐 Ingress Access: http://$INGRESS_HOST"
        print_status "   (Make sure '$INGRESS_HOST' points to your ingress controller)"
    fi
    
    # Port forwarding option
    print_status "🔗 Port Forward: kubectl port-forward -n $NAMESPACE service/${APP_NAME}-service 8080:80"
}

# Main deployment process
print_header "Starting Kubernetes Deployment for $APP_NAME"

# Apply manifests in order
print_status "Deploying to namespace: $NAMESPACE"

# 1. Namespace
apply_manifest "$K8S_DIR/namespace.yaml" "Namespace"

# 2. ConfigMap
apply_manifest "$K8S_DIR/configmap.yaml" "ConfigMap"

# 3. Deployment
apply_manifest "$K8S_DIR/deployment.yaml" "Deployment (Multi-Architecture)"

# 4. Service
apply_manifest "$K8S_DIR/service.yaml" "Services"

# 5. Ingress (optional)
if [ -f "$K8S_DIR/ingress.yaml" ]; then
    apply_manifest "$K8S_DIR/ingress.yaml" "Ingress"
fi

# Wait for deployment to be ready
wait_for_deployment

# Show status
show_status

# Show access information
show_access_info

# Final success message
if [ "$DRY_RUN" = true ]; then
    print_status "✅ Dry run completed successfully!"
else
    print_status "✅ Deployment completed successfully!"
    echo ""
    print_status "Useful commands:"
    echo "  View pods:        kubectl get pods -n $NAMESPACE"
    echo "  View logs:        kubectl logs -n $NAMESPACE deployment/$APP_NAME"
    echo "  Scale app:        kubectl scale deployment/$APP_NAME --replicas=5 -n $NAMESPACE"
    echo "  Delete app:       kubectl delete namespace $NAMESPACE"
fi