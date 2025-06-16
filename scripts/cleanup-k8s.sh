#!/bin/bash

# Cleanup Ramayanam from Kubernetes
set -e

echo "Cleaning up Ramayanam from Kubernetes..."

# Delete resources in reverse order
kubectl delete -f k8s/ingress.yaml --ignore-not-found=true
kubectl delete -f k8s/service.yaml --ignore-not-found=true
kubectl delete -f k8s/deployment.yaml --ignore-not-found=true
kubectl delete -f k8s/configmap.yaml --ignore-not-found=true
kubectl delete -f k8s/namespace.yaml --ignore-not-found=true

echo "Cleanup completed!"