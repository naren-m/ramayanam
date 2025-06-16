# Ramayanam Deployment Guide

This guide covers deploying the Ramayanam application using Docker and Kubernetes.

## Prerequisites

- Docker
- Kubernetes cluster (minikube, kind, or cloud provider)
- kubectl configured to access your cluster

## Quick Start

### 1. Build Docker Image

```bash
# Build the Docker image
./scripts/build-docker.sh

# Or manually:
docker build -t ramayanam:latest .
```

### 2. Run Locally with Docker

```bash
# Run with docker-compose (production)
docker-compose up

# Run with docker-compose (development)
docker-compose -f docker-compose.dev.yml up

# Or run directly
docker run -p 5000:5000 ramayanam:latest
```

### 3. Deploy to Kubernetes

```bash
# Deploy to Kubernetes
./scripts/deploy-k8s.sh

# Check deployment status
kubectl get pods -n ramayanam
kubectl get services -n ramayanam
```

### 4. Access the Application

#### Port Forward (Recommended for testing)
```bash
kubectl port-forward -n ramayanam service/ramayanam-service 8080:80
# Access at: http://localhost:8080
```

#### NodePort (Direct access)
```bash
# Access at: http://<node-ip>:30080
kubectl get nodes -o wide  # Get node IP
```

#### Ingress (Production)
```bash
# Add to /etc/hosts:
echo "127.0.0.1 ramayanam.local" >> /etc/hosts
# Access at: http://ramayanam.local
```

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Flask API      │    │   Data Files    │
│   (HTML/JS)     │◄───┤   (Python)       │◄───┤   (SQLite/Pkl)  │
│   Port 5000     │    │   Port 5000      │    │   /app/data     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_ENV` | `production` | Flask environment |
| `PORT` | `5000` | Application port |
| `LOG_LEVEL` | `INFO` | Logging level |
| `WORKERS` | `2` | Gunicorn workers |

### Kubernetes Resources

- **Namespace**: `ramayanam`
- **Deployment**: 2 replicas with rolling updates
- **Services**: ClusterIP and NodePort
- **Ingress**: nginx-based routing
- **ConfigMap**: Environment configuration

### Resource Limits

- **Memory**: 512Mi request, 1Gi limit
- **CPU**: 250m request, 500m limit

## Monitoring

### Health Checks

- **Liveness Probe**: `/api/ramayanam/kandas/1`
- **Readiness Probe**: `/api/ramayanam/kandas/1`

### Logging

```bash
# View application logs
kubectl logs -n ramayanam -l app=ramayanam -f

# View specific pod logs
kubectl logs -n ramayanam <pod-name>
```

## Scaling

```bash
# Scale replicas
kubectl scale deployment ramayanam-app --replicas=3 -n ramayanam

# Autoscaling (optional)
kubectl autoscale deployment ramayanam-app --cpu-percent=50 --min=1 --max=10 -n ramayanam
```

## Cleanup

```bash
# Remove from Kubernetes
./scripts/cleanup-k8s.sh

# Remove Docker images
docker rmi ramayanam:latest
```

## Troubleshooting

### Common Issues

1. **Pod not starting**
   ```bash
   kubectl describe pod <pod-name> -n ramayanam
   kubectl logs <pod-name> -n ramayanam
   ```

2. **Service not accessible**
   ```bash
   kubectl get endpoints -n ramayanam
   kubectl describe service ramayanam-service -n ramayanam
   ```

3. **Data not loading**
   - Check if data files are copied correctly in Docker image
   - Verify file paths in logs

### Development

For development with live reload:

```bash
# Use development compose
docker-compose -f docker-compose.dev.yml up

# Or run locally with virtual environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run.py
```

## Security

- Application runs as non-root user (uid: 1000)
- Security contexts applied to pods
- Read-only root filesystem (where possible)
- Resource limits enforced

## API Endpoints

- `GET /` - Frontend interface
- `GET /api/ramayanam/kandas/<id>` - Get kanda info
- `GET /api/ramayanam/slokas/fuzzy-search` - Search translations
- `GET /api/ramayanam/slokas/fuzzy-search-sanskrit` - Search Sanskrit text