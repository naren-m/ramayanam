# Ramayanam Digital Corpus

A comprehensive digital platform for searching and exploring the ancient Sanskrit epic Ramayana. This application provides both CLI tools and a web interface for searching through slokas (verses) in Sanskrit and English translations.

![Ramayana Search Interface](https://img.shields.io/badge/Ramayana-Digital%20Corpus-saffron?style=for-the-badge)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?style=flat-square&logo=docker)
![Kubernetes](https://img.shields.io/badge/Kubernetes-Ready-green?style=flat-square&logo=kubernetes)
![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python)

## 🌟 Features

- **Dual Search Interface**: Search in both Sanskrit (Devanagari) and English translations
- **Fuzzy Matching**: Find verses even with partial or approximate text
- **Kanda Filtering**: Filter searches by specific books (Kandas) of the Ramayana
- **Web Interface**: Modern, responsive web interface
- **CLI Tool**: Command-line interface for terminal usage
- **RESTful API**: Complete API for integration with other applications
- **Containerized**: Ready for Docker and Kubernetes deployment

## 📚 Data Coverage

The corpus includes all major Kandas (books) of Valmiki Ramayana:
- **Bala Kanda** (Book of Childhood)
- **Ayodhya Kanda** (Book of Ayodhya) 
- **Aranya Kanda** (Book of the Forest)
- **Kishkindha Kanda** (Book of Kishkindha)
- **Sundara Kanda** (Book of Beauty)
- **Yuddha Kanda** (Book of War)

Each verse includes:
- Original Sanskrit text in Devanagari script
- Word-by-word meaning
- English translation
- Verse numbering (Kanda.Sarga.Sloka format)

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd ramayanam

# Start the application
docker-compose up -d

# Access the web interface
open http://localhost:5000
```

### Option 2: Local Development

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python run.py

# Access the web interface
open http://localhost:5000
```

### Option 3: Kubernetes Deployment

```bash
# Build Docker image
./scripts/build-docker.sh

# Deploy to Kubernetes
./scripts/deploy-k8s.sh

# Access via port-forward
kubectl port-forward -n ramayanam service/ramayanam-service 8080:80
open http://localhost:8080
```

## 🖥️ Web Interface

The web application provides:

- **Search Box**: Enter Sanskrit text or English phrases
- **Kanda Filter**: Select specific books or search all
- **Results Display**: Shows matching verses with highlighted search terms
- **External Links**: Direct links to authoritative sources (valmiki.iitk.ac.in)
- **Responsive Design**: Works on desktop and mobile devices

### Example Searches

- **Sanskrit**: `राम` (rama), `सीता` (sita), `हनुमान` (hanuman)
- **English**: `rama`, `forest`, `monkey`, `demon`

## 🔧 API Reference

### Endpoints

#### Get Kanda Information
```http
GET /api/ramayanam/kandas/{kanda_id}
```

#### Get Specific Sloka
```http
GET /api/ramayanam/kandas/{kanda}/sargas/{sarga}/slokas/{sloka}
```

#### Fuzzy Search (English)
```http
GET /api/ramayanam/slokas/fuzzy-search?query={text}&kanda={number}
```

#### Fuzzy Search (Sanskrit)
```http
GET /api/ramayanam/slokas/fuzzy-search-sanskrit?query={text}&kanda={number}
```

### Response Format

```json
[
  {
    "sloka_number": "1.1.9",
    "ratio": 100,
    "sloka": "Sanskrit text in Devanagari",
    "meaning": "Word-by-word meaning",
    "translation": "English translation with <span class=\"highlight\">highlighted</span> terms"
  }
]
```

## 💻 CLI Usage

### Installation

```bash
pip install .
```

### Usage

```bash
# Get help
ramayanam --help

# Search functionality (to be implemented based on existing CLI)
ramayanam search "rama"
```

## 🐳 Docker Deployment

### Build Image

```bash
# Using script
./scripts/build-docker.sh

# Or manually
docker build -t ramayanam:latest .
```

### Run Container

```bash
# Run directly
docker run -p 5000:5000 ramayanam:latest

# Using docker-compose (production)
docker-compose up -d

# Using docker-compose (development)
docker-compose -f docker-compose.dev.yml up -d
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_ENV` | `production` | Flask environment |
| `PORT` | `5000` | Application port |
| `LOG_LEVEL` | `INFO` | Logging level |
| `WORKERS` | `2` | Gunicorn workers |

## ☸️ Kubernetes Deployment

### Prerequisites

- Kubernetes cluster (minikube, kind, or cloud provider)
- kubectl configured
- Docker image built

### Deploy to Kubernetes

```bash
# Deploy all components
./scripts/deploy-k8s.sh

# Check deployment status
kubectl get pods -n ramayanam
kubectl get services -n ramayanam
```

### Access Methods

#### 1. Port Forward (Development)
```bash
kubectl port-forward -n ramayanam service/ramayanam-service 8080:80
# Access: http://localhost:8080
```

#### 2. NodePort (Direct Access)
```bash
kubectl get nodes -o wide  # Get node IP
# Access: http://<node-ip>:30080
```

#### 3. Ingress (Production)
```bash
# Add to /etc/hosts
echo "127.0.0.1 ramayanam.local" >> /etc/hosts
# Access: http://ramayanam.local
```

### Kubernetes Resources

The deployment creates:
- **Namespace**: `ramayanam`
- **Deployment**: 2 replicas with rolling updates
- **Services**: ClusterIP and NodePort
- **ConfigMap**: Environment configuration
- **Ingress**: nginx-based routing (optional)

### Resource Limits

- **Memory**: 512Mi request, 1Gi limit
- **CPU**: 250m request, 500m limit

### Scaling

```bash
# Scale replicas
kubectl scale deployment ramayanam-app --replicas=3 -n ramayanam

# Autoscaling
kubectl autoscale deployment ramayanam-app --cpu-percent=50 --min=1 --max=10 -n ramayanam
```

## 🔍 Monitoring & Logging

### Health Checks

- **Liveness Probe**: `/api/ramayanam/kandas/1`
- **Readiness Probe**: `/api/ramayanam/kandas/1`
- **Health Check Interval**: 30s

### View Logs

```bash
# Docker
docker-compose logs -f

# Kubernetes
kubectl logs -n ramayanam -l app=ramayanam -f

# Specific pod
kubectl logs -n ramayanam <pod-name>
```

## 🧹 Cleanup

### Docker

```bash
# Stop containers
docker-compose down

# Remove images
docker rmi ramayanam:latest
```

### Kubernetes

```bash
# Remove all resources
./scripts/cleanup-k8s.sh

# Or manually
kubectl delete namespace ramayanam
```

## 🛠️ Development

### Project Structure

```
ramayanam/
├── api/                    # Flask API backend
│   ├── controllers/        # API route handlers
│   ├── models/            # Data models
│   ├── services/          # Business logic
│   └── app.py            # Flask application
├── slokas-frontend/       # Web frontend
│   ├── index.html        # Main interface
│   ├── script.js         # JavaScript functionality
│   └── styles.css        # Styling
├── data/                  # Corpus data
│   ├── slokas/           # Text files by Kanda/Sarga
│   ├── db/               # SQLite database
│   └── pkl/              # Pickle cache
├── k8s/                  # Kubernetes manifests
├── scripts/              # Deployment scripts
├── ramayanam/            # CLI tool
├── Dockerfile            # Container definition
├── docker-compose.yml    # Container orchestration
└── requirements.txt      # Python dependencies
```

### Running Tests

```bash
# Run basic tests
python -m pytest tests/

# Test API endpoints
python tests/test_e2e.py
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 🔒 Security

- **Non-root container**: Runs as user `app` (uid: 1000)
- **Security contexts**: Applied in Kubernetes
- **Resource limits**: Memory and CPU limits enforced
- **Health checks**: Proactive monitoring
- **No secrets in code**: Environment-based configuration

## 📖 Documentation

- **API Documentation**: See API Reference section above
- **Deployment Guide**: `DEPLOYMENT.md`
- **Kubernetes Setup**: `KUBERNETES_READY.md`

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests for any improvements.

### Areas for Contribution

- Additional search features
- Performance optimizations
- UI/UX improvements
- Additional export formats
- Mobile app development
- Advanced Sanskrit text processing

## 📄 License

This project is open source. Please respect the cultural and religious significance of the Ramayana text.

## 🙏 Acknowledgments

- Valmiki Ramayana text from authoritative sources
- IIT Kanpur for digital Ramayana resources
- Sanskrit scholars and translators
- Open source community

## 📞 Support

For issues and questions:
- Create an issue in the repository
- Check existing documentation
- Review deployment guides

---

**🕉️ May this digital preservation of the ancient wisdom serve seekers of knowledge and devotees alike.**