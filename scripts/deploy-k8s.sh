#!/bin/bash

# Deploy Ramayanam to Kubernetes
set -e

echo "Deploying Ramayanam to Kubernetes..."

# Apply namespace first
kubectl apply -f k8s/namespace.yaml

# Apply ConfigMap
kubectl apply -f k8s/configmap.yaml

# Apply Deployment
kubectl apply -f k8s/deployment.yaml

# Apply Service
kubectl apply -f k8s/service.yaml

# Apply Ingress (optional)
kubectl apply -f k8s/ingress.yaml

echo ""
echo "Deployment completed!"
echo ""
echo "Check status:"
echo "  kubectl get pods -n ramayanam"
echo "  kubectl get services -n ramayanam"
echo ""
echo "Access application:"
echo "  kubectl port-forward -n ramayanam service/ramayanam-service 8080:80"
echo "  Then open: http://localhost:8080"
echo ""
echo "Or if using NodePort:"
echo "  Access via: http://<node-ip>:30080"