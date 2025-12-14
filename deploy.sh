#!/bin/bash

# Pesabu Backend Deployment Script

set -e

echo "🚀 Starting Pesabu Backend Deployment..."

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p output
mkdir -p data
chmod 755 output data

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Build and start containers
echo "🔨 Building Docker image..."
docker-compose build

echo "🚀 Starting containers..."
docker-compose up -d

# Wait for service to be healthy
echo "⏳ Waiting for service to be ready..."
sleep 5

# Check if service is running
if curl -f http://localhost:8000/ &> /dev/null; then
    echo "✅ Backend is running successfully!"
    echo "📍 API available at: http://localhost:8000"
    echo "📚 API docs available at: http://localhost:8000/docs"
    echo ""
    echo "To view logs: docker-compose logs -f"
    echo "To stop: docker-compose down"
else
    echo "⚠️  Service might still be starting. Check logs with: docker-compose logs -f"
fi

