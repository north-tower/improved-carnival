# Quick Start Guide - Pesabu Backend

## Deploy with Docker Compose (Easiest)

```bash
# 1. Navigate to the backend directory
cd pesabu-backend-main

# 2. Run the deployment script
./deploy.sh

# OR manually:
docker-compose up -d
```

## Deploy with Docker (Manual)

```bash
# 1. Build the image
docker build -t pesabu-backend .

# 2. Run the container
docker run -d \
  --name pesabu-backend \
  -p 8000:8000 \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/data:/app/data \
  pesabu-backend
```

## Verify Deployment

```bash
# Check if container is running
docker ps

# Test the API
curl http://localhost:8000/

# View API documentation
# Open in browser: http://localhost:8000/docs
```

## Common Commands

```bash
# View logs
docker-compose logs -f

# Stop the service
docker-compose down

# Restart the service
docker-compose restart

# Rebuild after code changes
docker-compose up -d --build
```

## Access Points

- **API Base**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Troubleshooting

```bash
# Check logs for errors
docker-compose logs backend

# Check if port is in use
lsof -i :8000

# Rebuild without cache
docker-compose build --no-cache
```

For more details, see [DEPLOYMENT.md](./DEPLOYMENT.md)

