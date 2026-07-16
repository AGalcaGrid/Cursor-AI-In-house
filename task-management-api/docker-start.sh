#!/bin/bash

# Docker Quick Start Script for Task Management API
# This script starts all services using Docker Compose

echo "🐳 Starting Task Management API with Docker..."
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed"
    echo "Please install Docker Compose (usually included with Docker Desktop)"
    exit 1
fi

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    echo "❌ Docker daemon is not running"
    echo "Please start Docker Desktop or the Docker daemon"
    exit 1
fi

echo "✅ Docker is installed and running"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "✅ .env file created"
    echo "⚠️  You may want to edit .env to configure email settings"
    echo ""
fi

# Stop any existing containers
echo "🛑 Stopping any existing containers..."
docker-compose down &> /dev/null
echo ""

# Build images
echo "🔨 Building Docker images..."
docker-compose build
if [ $? -ne 0 ]; then
    echo "❌ Failed to build Docker images"
    exit 1
fi
echo "✅ Images built successfully"
echo ""

# Start services
echo "🚀 Starting services..."
docker-compose up -d
if [ $? -ne 0 ]; then
    echo "❌ Failed to start services"
    exit 1
fi
echo ""

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 5

# Check service status
echo ""
echo "📊 Service Status:"
docker-compose ps
echo ""

# Check health
echo "🏥 Health Checks:"
echo ""

# Check Redis
echo -n "Redis: "
if docker-compose exec -T redis redis-cli ping &> /dev/null; then
    echo "✅ Healthy"
else
    echo "❌ Not responding"
fi

# Check API
echo -n "API: "
if curl -s http://localhost:5003/api/auth/health &> /dev/null; then
    echo "✅ Healthy"
else
    echo "⚠️  Starting up... (may take a few seconds)"
fi

# Check Celery Worker
echo -n "Celery Worker: "
if docker-compose logs celery-worker 2>&1 | grep -q "ready"; then
    echo "✅ Running"
else
    echo "⚠️  Starting up..."
fi

echo ""
echo "✅ All services started!"
echo ""
echo "📝 Service URLs:"
echo "   API:            http://localhost:5003"
echo "   Health Check:   http://localhost:5003/api/auth/health"
echo "   Swagger Docs:   http://localhost:5003/apidocs"
echo "   Redis:          localhost:6379"
echo ""
echo "📋 Useful Commands:"
echo "   View logs:      docker-compose logs -f"
echo "   Stop services:  docker-compose down"
echo "   Restart:        docker-compose restart"
echo "   Run tests:      docker-compose exec api pytest"
echo ""
echo "📚 See DOCKER_GUIDE.md for detailed documentation"
echo ""
echo "🎉 Ready to use! Try:"
echo "   curl http://localhost:5003/api/auth/health"
echo ""
