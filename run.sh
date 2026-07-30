#!/bin/bash

# AURA v1.0 Local Development Startup Script
# Usage: ./run.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Starting AURA v1.0 Platform..."
echo ""

# Check for docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker to run AURA."
    exit 1
fi

# Check for docker-compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose not found. Please install Docker Compose to run AURA."
    exit 1
fi

# Build and start services (dev mode - skip desktop app)
echo "📦 Building Docker images..."
docker-compose -f docker-compose.yml -f docker-compose.dev.yml build --quiet

echo "🐳 Starting services..."
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 5

# Check health
echo ""
echo "🏥 Checking service health..."

# Backend health check
for i in {1..10}; do
    if curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then
        echo "✅ Backend: Running on http://localhost:8000"
        break
    fi
    if [ $i -eq 10 ]; then
        echo "❌ Backend: Failed to start"
        echo ""
        echo "Logs:"
        docker-compose -f docker-compose.yml -f docker-compose.dev.yml logs backend
        exit 1
    fi
    sleep 2
done

# Postgres health check
for i in {1..10}; do
    if docker-compose -f docker-compose.yml -f docker-compose.dev.yml exec -T postgres pg_isready -U aura_user > /dev/null 2>&1; then
        echo "✅ PostgreSQL: Running on localhost:5432"
        break
    fi
    if [ $i -eq 10 ]; then
        echo "⚠️  PostgreSQL: Timeout waiting for ready"
    fi
    sleep 2
done

# Redis health check
for i in {1..10}; do
    if docker-compose -f docker-compose.yml -f docker-compose.dev.yml exec -T redis redis-cli ping > /dev/null 2>&1; then
        echo "✅ Redis: Running on localhost:6379"
        break
    fi
    if [ $i -eq 10 ]; then
        echo "⚠️  Redis: Timeout waiting for ready"
    fi
    sleep 2
done

# RabbitMQ health check
for i in {1..10}; do
    if curl -s http://localhost:15672 > /dev/null 2>&1; then
        echo "✅ RabbitMQ: Running on localhost:5672 (admin: http://localhost:15672)"
        break
    fi
    if [ $i -eq 10 ]; then
        echo "⚠️  RabbitMQ: Timeout waiting for ready"
    fi
    sleep 2
done

echo ""
echo "========================================="
echo "✅ AURA v1.0 is running!"
echo "========================================="
echo ""
echo "🌐 Web Dashboard: http://localhost:8000"
echo "📚 API Docs:      http://localhost:8000/docs"
echo "🔌 Backend API:   http://localhost:8000/api/v1"
echo ""
echo "💾 Database:      postgresql://aura_user@localhost:5432/aura"
echo "🔴 Redis:         redis://localhost:6379"
echo "🐰 RabbitMQ:      http://localhost:15672 (guest/guest)"
echo ""
echo "To stop the services, run: docker-compose down"
echo "To view logs, run:        docker-compose logs -f"
echo ""
