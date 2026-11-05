# AURA v1.0 Local Development Startup Script for Windows
# Usage: .\run.ps1

$ErrorActionPreference = "Stop"

Write-Host "🚀 Starting AURA v1.0 Platform..." -ForegroundColor Green
Write-Host ""

# Check for docker
$dockerExists = $null -ne (Get-Command docker -ErrorAction SilentlyContinue)
if (-not $dockerExists) {
    Write-Host "❌ Docker not found. Please install Docker Desktop to run AURA." -ForegroundColor Red
    exit 1
}

# Check for docker-compose
$dockerComposeExists = $null -ne (Get-Command docker-compose -ErrorAction SilentlyContinue)
if (-not $dockerComposeExists) {
    Write-Host "❌ Docker Compose not found. Please install Docker Desktop to run AURA." -ForegroundColor Red
    exit 1
}

# Build and start services (dev mode - skip desktop app)
Write-Host "📦 Building Docker images..." -ForegroundColor Yellow
docker-compose -f docker-compose.yml -f docker-compose.dev.yml build --quiet

Write-Host "🐳 Starting services..." -ForegroundColor Yellow
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Wait for services to be healthy
Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Check health
Write-Host ""
Write-Host "🏥 Checking service health..." -ForegroundColor Yellow

# Backend health check
$backendReady = $false
for ($i = 0; $i -lt 10; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/health" -UseBasicParsing -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ Backend: Running on http://localhost:8000" -ForegroundColor Green
            $backendReady = $true
            break
        }
    }
    catch { }

    if ($i -eq 9) {
        Write-Host "❌ Backend: Failed to start" -ForegroundColor Red
        Write-Host ""
        Write-Host "Logs:" -ForegroundColor Red
        docker-compose logs backend
        exit 1
    }
    Start-Sleep -Seconds 2
}

# Postgres health check
for ($i = 0; $i -lt 10; $i++) {
    try {
        docker-compose exec -T postgres pg_isready -U aura_user | Out-Null 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ PostgreSQL: Running on localhost:5432" -ForegroundColor Green
            break
        }
    }
    catch { }

    if ($i -eq 9) {
        Write-Host "⚠️  PostgreSQL: Timeout waiting for ready" -ForegroundColor Yellow
    }
    Start-Sleep -Seconds 2
}

# Redis health check
for ($i = 0; $i -lt 10; $i++) {
    try {
        docker-compose exec -T redis redis-cli ping | Out-Null 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Redis: Running on localhost:6379" -ForegroundColor Green
            break
        }
    }
    catch { }

    if ($i -eq 9) {
        Write-Host "⚠️  Redis: Timeout waiting for ready" -ForegroundColor Yellow
    }
    Start-Sleep -Seconds 2
}

# RabbitMQ health check
for ($i = 0; $i -lt 10; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:15672" -UseBasicParsing -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ RabbitMQ: Running on localhost:5672 (admin: http://localhost:15672)" -ForegroundColor Green
            break
        }
    }
    catch { }

    if ($i -eq 9) {
        Write-Host "⚠️  RabbitMQ: Timeout waiting for ready" -ForegroundColor Yellow
    }
    Start-Sleep -Seconds 2
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Green
Write-Host "✅ AURA v1.0 is running!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Web Dashboard: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 API Docs:      http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "🔌 Backend API:   http://localhost:8000/api/v1" -ForegroundColor Cyan
Write-Host ""
Write-Host "💾 Database:      postgresql://aura_user@localhost:5432/aura" -ForegroundColor Cyan
Write-Host "🔴 Redis:         redis://localhost:6379" -ForegroundColor Cyan
Write-Host "🐰 RabbitMQ:      http://localhost:15672 (guest/guest)" -ForegroundColor Cyan
Write-Host ""
Write-Host "To stop the services, run: docker-compose down" -ForegroundColor Yellow
Write-Host "To view logs, run:        docker-compose logs -f" -ForegroundColor Yellow
Write-Host ""
