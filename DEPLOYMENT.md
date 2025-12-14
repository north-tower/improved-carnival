# Pesabu Backend Deployment Guide

This guide explains how to deploy the Pesabu backend using Docker.

## Prerequisites

- Docker installed (version 20.10 or later)
- Docker Compose installed (version 1.29 or later)

## Quick Start

### 1. Build and Run with Docker Compose

```bash
# Navigate to the backend directory
cd pesabu-backend-main

# Build and start the container
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the container
docker-compose down
```

### 2. Build and Run with Docker (Manual)

```bash
# Build the image
docker build -t pesabu-backend .

# Run the container
docker run -d \
  --name pesabu-backend \
  -p 8000:8000 \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/data:/app/data \
  pesabu-backend

# View logs
docker logs -f pesabu-backend

# Stop the container
docker stop pesabu-backend
docker rm pesabu-backend
```

## Configuration

### Port Configuration

The backend runs on port `8000` by default. To change the port:

**Docker Compose:**
```yaml
ports:
  - "YOUR_PORT:8000"
```

**Docker Run:**
```bash
docker run -p YOUR_PORT:8000 pesabu-backend
```

### Environment Variables

Currently, the backend uses SQLite by default. To customize:

1. Create a `.env` file (if needed in the future)
2. Update `docker-compose.yml` to include environment variables:
```yaml
environment:
  - DATABASE_URL=sqlite:///./data/sql.db
  - PYTHONUNBUFFERED=1
```

## API Endpoints

Once deployed, the API will be available at:

- **Base URL**: `http://localhost:8000`
- **API Docs**: `http://localhost:8000/docs` (Swagger UI)
- **ReDoc**: `http://localhost:8000/redoc`

## Health Check

The container includes a health check. Verify it's running:

```bash
# Check container status
docker ps

# Check health
docker inspect pesabu-backend | grep -A 10 Health

# Test the API
curl http://localhost:8000/
```

## Production Deployment

### 1. Using Docker Compose (Recommended)

```bash
# Build for production
docker-compose -f docker-compose.yml build

# Run in detached mode
docker-compose -f docker-compose.yml up -d

# View logs
docker-compose logs -f backend
```

### 2. Using Docker Swarm

```bash
# Initialize swarm (if not already)
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml pesabu-backend

# Check services
docker service ls
```

### 3. Using Kubernetes

Create a `k8s-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pesabu-backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: pesabu-backend
  template:
    metadata:
      labels:
        app: pesabu-backend
    spec:
      containers:
      - name: backend
        image: pesabu-backend:latest
        ports:
        - containerPort: 8000
        volumeMounts:
        - name: output
          mountPath: /app/output
---
apiVersion: v1
kind: Service
metadata:
  name: pesabu-backend-service
spec:
  selector:
    app: pesabu-backend
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

## Troubleshooting

### Container won't start

```bash
# Check logs
docker-compose logs backend

# Check if port is already in use
lsof -i :8000

# Rebuild without cache
docker-compose build --no-cache
```

### Permission issues

```bash
# Fix output directory permissions
sudo chown -R $USER:$USER ./output
sudo chmod -R 755 ./output
```

### Database issues

If using SQLite, ensure the data directory is mounted and has write permissions:

```bash
mkdir -p data
chmod 755 data
```

## Updating the Application

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose up -d --build

# Or for manual Docker
docker build -t pesabu-backend .
docker stop pesabu-backend
docker rm pesabu-backend
docker run -d --name pesabu-backend -p 8000:8000 \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/data:/app/data \
  pesabu-backend
```

## Monitoring

### View Real-time Logs

```bash
# Docker Compose
docker-compose logs -f backend

# Docker
docker logs -f pesabu-backend
```

### Resource Usage

```bash
# Container stats
docker stats pesabu-backend
```

## Security Considerations

1. **Change CORS settings** in `app/main.py` for production:
   ```python
   origins = ["https://yourdomain.com"]
   ```

2. **Use environment variables** for sensitive data

3. **Enable HTTPS** using a reverse proxy (nginx, traefik)

4. **Limit resource usage**:
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '1'
         memory: 1G
   ```

## Reverse Proxy Setup (Nginx)

Example nginx configuration:

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Backup

### Database Backup (SQLite)

```bash
# Backup database
docker exec pesabu-backend cp /app/data/sql.db /app/data/sql.db.backup

# Or from host
docker cp pesabu-backend:/app/data/sql.db ./backups/sql.db.$(date +%Y%m%d)
```

## Support

For issues or questions, check the logs first:
```bash
docker-compose logs backend
```

