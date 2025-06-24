#!/bin/bash

# Kubernetes Deployment Script for Ramayanam Application
# This script deploys the Ramayanam application to a Kubernetes cluster

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
K8S_DIR="$PROJECT_ROOT/k8s"

# Configuration
NAMESPACE="ramayanam"
APP_NAME="ramayanam-app"
IMAGE_TAG="latest"

echo -e "${BLUE}🚀 Deploying Ramayanam Application to Kubernetes${NC}"
echo "============================================"

# Function to check if kubectl is available
check_kubectl() {
    if ! command -v kubectl &> /dev/null; then
        echo -e "${RED}❌ kubectl is not installed or not in PATH${NC}"
        echo "Please install kubectl: https://kubernetes.io/docs/tasks/tools/"
        exit 1
    fi
    echo -e "${GREEN}✅ kubectl is available${NC}"
}

# Function to check if cluster is accessible
check_cluster() {
    echo -e "${YELLOW}🔍 Checking cluster connectivity...${NC}"
    if ! kubectl cluster-info &> /dev/null; then
        echo -e "${RED}❌ Cannot connect to Kubernetes cluster${NC}"
        echo "Please ensure your kubectl is configured and cluster is accessible"
        exit 1
    fi
    echo -e "${GREEN}✅ Cluster is accessible${NC}"
    kubectl cluster-info | grep "running at"
}

# Function to build Docker image
build_image() {
    echo -e "${YELLOW}🏗️  Building Docker image...${NC}"
    cd "$PROJECT_ROOT"
    
    if docker build -t "ramayanam:${IMAGE_TAG}" -f Dockerfile.dev .; then
        echo -e "${GREEN}✅ Docker image built successfully${NC}"
    else
        echo -e "${RED}❌ Failed to build Docker image${NC}"
        exit 1
    fi
    
    # Tag for local use (if using local registry)
    docker tag "ramayanam:${IMAGE_TAG}" "ramayanam:latest"
    echo -e "${GREEN}✅ Image tagged as ramayanam:${IMAGE_TAG} and ramayanam:latest${NC}"
}


# Function to apply Kubernetes manifests
deploy_manifests() {
    echo -e "${YELLOW}📦 Applying Kubernetes manifests...${NC}"
    
    # Apply in order: namespace, configmap, deployment, service, ingress
    echo "Creating namespace..."
    kubectl apply -f "$K8S_DIR/namespace.yaml"
    
    echo "Creating ConfigMap..."
    kubectl apply -f "$K8S_DIR/configmap.yaml"
    
    echo "Creating Deployment..."
    kubectl apply -f "$K8S_DIR/deployment.yaml"
    
    echo "Creating Services..."
    kubectl apply -f "$K8S_DIR/service.yaml"
    
    echo "Creating Ingress..."
    kubectl apply -f "$K8S_DIR/ingress.yaml"
    
    echo -e "${GREEN}✅ All manifests applied successfully${NC}"
}

# Function to wait for deployment to be ready
wait_for_deployment() {
    echo -e "${YELLOW}⏳ Waiting for deployment to be ready...${NC}"
    
    if kubectl wait --for=condition=available --timeout=300s deployment/$APP_NAME -n $NAMESPACE; then
        echo -e "${GREEN}✅ Deployment is ready${NC}"
    else
        echo -e "${RED}❌ Deployment failed to become ready within 5 minutes${NC}"
        echo "Checking pod status..."
        kubectl get pods -n $NAMESPACE
        echo "Recent events:"
        kubectl get events -n $NAMESPACE --sort-by=.metadata.creationTimestamp | tail -10
        exit 1
    fi
}

# Function to show deployment status
show_status() {
    echo -e "${BLUE}📊 Deployment Status${NC}"
    echo "===================="
    
    echo -e "\n${YELLOW}Pods:${NC}"
    kubectl get pods -n $NAMESPACE -o wide
    
    echo -e "\n${YELLOW}Services:${NC}"
    kubectl get services -n $NAMESPACE
    
    echo -e "\n${YELLOW}Ingress:${NC}"
    kubectl get ingress -n $NAMESPACE
    
    echo -e "\n${YELLOW}Deployment Details:${NC}"
    kubectl describe deployment $APP_NAME -n $NAMESPACE | grep -A 5 "Replicas"
}

# Function to show access information
show_access_info() {
    echo -e "\n${BLUE}🌐 Access Information${NC}"
    echo "====================="
    
    # Get NodePort
    NODEPORT=$(kubectl get service ramayanam-nodeport -n $NAMESPACE -o jsonpath='{.spec.ports[0].nodePort}' 2>/dev/null || echo "30080")
    
    echo -e "${GREEN}Application Endpoints:${NC}"
    echo "1. Port Forward: kubectl port-forward service/ramayanam-service -n $NAMESPACE 8080:80"
    echo "   Then access: http://localhost:8080"
    echo "2. NodePort Service: http://<node-ip>:$NODEPORT"
    echo "3. Ingress: http://ramayanam.local (add to /etc/hosts)"
    
    echo -e "\n${GREEN}API Endpoints (after port-forward):${NC}"
    echo "- Health Check: http://localhost:8080/api/ramayanam/kandas/1"
    echo "- Search Stats: http://localhost:8080/api/ramayanam/search/stats"
    echo "- Translation Search: http://localhost:8080/api/ramayanam/slokas/fuzzy-search?query=rama"
    echo "- Sanskrit Search: http://localhost:8080/api/ramayanam/slokas/fuzzy-search-sanskrit?query=dharma"
    echo "- Streaming Search: http://localhost:8080/api/ramayanam/slokas/fuzzy-search-stream?query=rama"
}

# Function to run quick tests
run_tests() {
    echo -e "\n${YELLOW}🧪 Running quick health checks...${NC}"
    
    # Set up port forward in background
    kubectl port-forward service/ramayanam-service -n $NAMESPACE 8081:80 &
    PF_PID=$!
    
    # Wait a moment for port forward to establish
    sleep 3
    
    # Test basic endpoint
    if curl -s -f http://localhost:8081/api/ramayanam/kandas/1 > /dev/null; then
        echo -e "${GREEN}✅ Health check passed${NC}"
    else
        echo -e "${RED}❌ Health check failed${NC}"
    fi
    
    # Test performance endpoint
    if curl -s -f http://localhost:8081/api/ramayanam/search/stats > /dev/null; then
        echo -e "${GREEN}✅ Performance endpoint available${NC}"
    else
        echo -e "${YELLOW}⚠️  Performance endpoint not ready yet${NC}"
    fi
    
    # Kill port forward
    kill $PF_PID 2>/dev/null || true
}

# Main execution
main() {
    echo -e "${BLUE}Starting deployment process...${NC}"
    
    # Parse command line arguments
    SKIP_BUILD=false
    SKIP_WAIT=false
    RUN_TESTS=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-build)
                SKIP_BUILD=true
                shift
                ;;
            --skip-wait)
                SKIP_WAIT=true
                shift
                ;;
            --test)
                RUN_TESTS=true
                shift
                ;;
            -h|--help)
                echo "Usage: $0 [OPTIONS]"
                echo "Options:"
                echo "  --skip-build    Skip Docker image building"
                echo "  --skip-wait     Skip waiting for deployment readiness"
                echo "  --test          Run quick health checks after deployment"
                echo "  -h, --help      Show this help message"
                exit 0
                ;;
            *)
                echo "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    # Execute deployment steps
    check_kubectl
    check_cluster
    
    if [ "$SKIP_BUILD" = false ]; then
        build_image
        load_image_to_kind
    else
        echo -e "${YELLOW}⏭️  Skipping Docker build${NC}"
    fi
    
    deploy_manifests
    
    if [ "$SKIP_WAIT" = false ]; then
        wait_for_deployment
    else
        echo -e "${YELLOW}⏭️  Skipping deployment wait${NC}"
    fi
    
    show_status
    show_access_info
    
    if [ "$RUN_TESTS" = true ]; then
        run_tests
    fi
    
    echo -e "\n${GREEN}🎉 Deployment completed successfully!${NC}"
    echo -e "${BLUE}Use 'kubectl logs -f deployment/$APP_NAME -n $NAMESPACE' to view logs${NC}"
}

# Trap cleanup on script exit
trap 'echo -e "\n${YELLOW}Script interrupted${NC}"' INT

# Run main function
main "$@"
