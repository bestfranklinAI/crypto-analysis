# Deployment Guide

## Overview

This guide covers deploying the Market Data Engine in various environments:
1. **Local Development** (for testing)
2. **Docker** (for containerized deployment)
3. **Cloud Deployment** (AWS, Azure, GCP)

---

## Prerequisites

### System Requirements
- **OS**: Linux, macOS, or Windows (WSL2 recommended)
- **CPU**: 2+ cores
- **RAM**: 2GB minimum, 4GB recommended
- **Disk**: 1GB for application + logs

### Software Requirements
- Python 3.13+
- C++17 compiler (GCC 7+, Clang 5+, MSVC 2017+)
- CMake 3.18+
- Git

---

## Local Development Setup

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/market-data-engine.git
cd market-data-engine
```

### 2. Create Virtual Environment

```bash
python3.13 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Build C++ Extension

```bash
cd market_engine
mkdir build
cd build
cmake ..
make
cd ../..

# Copy compiled module to project root
cp market_engine/build/market_engine*.so .  # Linux/macOS
# Or: cp market_engine/build/Release/market_engine.pyd .  # Windows
```

**Verify C++ module**:
```bash
python -c "import market_engine; print('C++ module loaded successfully')"
```

### 5. Configure Environment

```bash
cp .env.example .env
# Edit .env with your preferred settings
```

Key configuration options:
```ini
SYMBOLS=BTCUSDT,ETHUSDT,BNBUSDT
LOG_LEVEL=INFO
API_PORT=8000
```

### 6. Run the Application

```bash
python main.py
```

**Expected output**:
```
INFO: Starting Market Data Engine v0.1.0
INFO: Connecting to Binance WebSocket...
INFO: Connected to Binance for symbols: BTCUSDT, ETHUSDT
INFO: FastAPI server running on http://0.0.0.0:8000
```

### 7. Verify Deployment

Open browser to: `http://localhost:8000/docs`

Or test with curl:
```bash
curl http://localhost:8000/health
```

---

## Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.13-slim

# Install build dependencies
RUN apt-get update && apt-get install -y \
    g++ \
    cmake \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY requirements.txt .
COPY pyproject.toml .
COPY app/ ./app/
COPY market_engine/ ./market_engine/
COPY main.py .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Build C++ extension
RUN cd market_engine && \
    mkdir build && \
    cd build && \
    cmake .. && \
    make && \
    cp market_engine*.so /app/

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["python", "main.py"]
```

### Build and Run

```bash
# Build image
docker build -t market-data-engine:latest .

# Run container
docker run -d \
  --name market-engine \
  -p 8000:8000 \
  -e SYMBOLS=BTCUSDT,ETHUSDT \
  -v $(pwd)/logs:/app/logs \
  market-data-engine:latest

# View logs
docker logs -f market-engine

# Stop container
docker stop market-engine
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  market-engine:
    build: .
    container_name: market-data-engine
    ports:
      - "8000:8000"
    environment:
      - SYMBOLS=BTCUSDT,ETHUSDT,BNBUSDT,ADAUSDT,SOLUSDT
      - LOG_LEVEL=INFO
      - DATABASE_URL=sqlite+aiosqlite:///./data/market_data.db
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s

  # Optional: Nginx reverse proxy
  nginx:
    image: nginx:alpine
    container_name: market-engine-nginx
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - market-engine
    restart: unless-stopped
```

**Run with Docker Compose**:
```bash
docker-compose up -d
docker-compose logs -f
```

---

## Production Deployment

### Option 1: AWS EC2

**1. Launch EC2 Instance**
- Instance type: `t3.small` or larger
- AMI: Ubuntu 22.04 LTS
- Security group: Allow inbound on port 8000

**2. SSH and Setup**
```bash
ssh ubuntu@your-ec2-public-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu
newgrp docker

# Clone and deploy
git clone https://github.com/yourusername/market-data-engine.git
cd market-data-engine
docker-compose up -d
```

**3. Configure Domain (Optional)**
- Point DNS A record to EC2 public IP
- Use Nginx with Let's Encrypt for HTTPS

---

### Option 2: AWS ECS Fargate

**1. Create ECR Repository**
```bash
aws ecr create-repository --repository-name market-data-engine
```

**2. Build and Push Image**
```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com

# Build and tag
docker build -t market-data-engine .
docker tag market-data-engine:latest YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/market-data-engine:latest

# Push
docker push YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/market-data-engine:latest
```

**3. Create ECS Task Definition**

Create `task-definition.json`:
```json
{
  "family": "market-data-engine",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "market-engine",
      "image": "YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/market-data-engine:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "SYMBOLS",
          "value": "BTCUSDT,ETHUSDT"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/market-data-engine",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

**4. Create ECS Service**
```bash
aws ecs create-service \
  --cluster your-cluster \
  --service-name market-data-engine \
  --task-definition market-data-engine \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

---

### Option 3: Kubernetes (GKE, EKS, AKS)

**deployment.yaml**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: market-data-engine
spec:
  replicas: 2
  selector:
    matchLabels:
      app: market-engine
  template:
    metadata:
      labels:
        app: market-engine
    spec:
      containers:
      - name: market-engine
        image: your-registry/market-data-engine:latest
        ports:
        - containerPort: 8000
        env:
        - name: SYMBOLS
          value: "BTCUSDT,ETHUSDT"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
---
apiVersion: v1
kind: Service
metadata:
  name: market-engine-service
spec:
  selector:
    app: market-engine
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

**Deploy**:
```bash
kubectl apply -f deployment.yaml
kubectl get services  # Get LoadBalancer IP
```

---

## Monitoring and Logging

### Logging Configuration

**Production logging** (`.env`):
```ini
LOG_LEVEL=WARNING
LOG_FORMAT=json
LOG_OUTPUT=/var/log/market-engine/app.log
```

### Metrics Collection (Optional)

Use Prometheus for metrics:

1. Install Prometheus Python client:
```bash
pip install prometheus-client
```

2. Expose metrics endpoint in `app/api_server.py`

3. Configure Prometheus to scrape:
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'market-engine'
    static_configs:
      - targets: ['localhost:8000']
```

---

## Backup and Recovery

### Database Backup

```bash
# Backup SQLite database
cp market_data.db backups/market_data_$(date +%Y%m%d).db

# Automated daily backups (cron)
0 2 * * * cp /app/market_data.db /backups/market_data_$(date +\%Y\%m\%d).db
```

### Disaster Recovery

1. **State**: All indicator state is in-memory; restart rebuilds from live data
2. **Historical data**: Backup `market_data.db` regularly
3. **Configuration**: Keep `.env` in version control (without secrets) or use AWS Secrets Manager

---

## Scaling Considerations

### Horizontal Scaling

**Challenge**: In-memory state per instance

**Solutions**:
1. **Symbol sharding**: Route symbols to specific instances via load balancer
2. **Shared cache**: Use Redis for indicator snapshots
3. **Message queue**: Use RabbitMQ/Kafka for trade distribution

### Vertical Scaling

| Workload | CPU | Memory | Recommendation |
|----------|-----|--------|----------------|
| 5 symbols | 1 core | 1GB | `t3.small` |
| 20 symbols | 2 cores | 2GB | `t3.medium` |
| 50 symbols | 4 cores | 4GB | `t3.large` |

---

## Troubleshooting

### Common Issues

**1. C++ module import error**
```
ImportError: No module named 'market_engine'
```
**Solution**: Rebuild C++ module and copy to project root

**2. Binance connection refused**
```
ERROR: Failed to connect to Binance WebSocket
```
**Solution**: Check internet connection, verify `BINANCE_WS_URL` in `.env`

**3. Port already in use**
```
ERROR: [Errno 48] Address already in use
```
**Solution**: Change `API_PORT` in `.env` or kill process using port 8000

**4. High memory usage**
```
WARNING: Memory usage above 80%
```
**Solution**: Reduce `MAX_TRADE_WINDOW` or number of `SYMBOLS`

---

## Security Checklist

- [ ] Run as non-root user in production
- [ ] Use secrets manager for sensitive config (future)
- [ ] Enable HTTPS with valid SSL certificate
- [ ] Configure firewall to allow only ports 80/443
- [ ] Keep dependencies updated (`pip list --outdated`)
- [ ] Enable rate limiting on API endpoints
- [ ] Set up monitoring and alerting
- [ ] Implement log rotation to prevent disk fill

---

## Updating the Application

```bash
# Pull latest code
git pull origin main

# Rebuild C++ module if changed
cd market_engine/build
cmake ..
make
cp market_engine*.so ../..

# Restart service
docker-compose down
docker-compose up -d --build
```

---

## Support and Further Reading

- **GitHub Issues**: [github.com/yourusername/market-data-engine/issues](https://github.com/yourusername/market-data-engine/issues)
- **Binance API Docs**: [binance-docs.github.io/apidocs](https://binance-docs.github.io/apidocs)
- **FastAPI Docs**: [fastapi.tiangolo.com](https://fastapi.tiangolo.com)
- **pybind11 Docs**: [pybind11.readthedocs.io](https://pybind11.readthedocs.io)
