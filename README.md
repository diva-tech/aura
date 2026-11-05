# AURA v1.0

**AI Platform for Content Creators** — Intelligent video analysis, recommendations, and multi-platform publishing.

AURA is a production-ready monorepo foundation for an AI-powered content creation platform with 14 milestones, 20+ autonomous agents, 30+ integrated providers, and a complete learning feedback loop.

## 🚀 Quick Start

### One-Command Startup

**macOS/Linux:**

```bash
git clone <repo>
cd aura
./run.sh
# Open http://localhost:8000
```

**Windows:**

```powershell
git clone <repo>
cd aura
.\run.ps1
# Open http://localhost:8000
```

### Or with Docker Compose directly:

```bash
docker-compose up --build
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Or with Make:

```bash
make up
make logs
# In another terminal: make test
```

## 📊 What's Included

This repository provides:

- **Backend**: FastAPI with clean architecture, 14 milestones, production-ready
- **Dashboard**: Real-time web UI for exploring platform, architecture, and metrics
- **Infrastructure**: Docker Compose for PostgreSQL, Redis, RabbitMQ, and Ollama
- **Logging**: Structured JSON logging with rotation and audit trails
- **Testing**: 300+ tests, 80%+ code coverage, comprehensive integration tests
- **Documentation**: 10 Architecture Decision Records (ADRs), comprehensive guides
- **Features**: Video analysis, AI recommendations, multi-platform publishing, learning loop

## 🎯 Platform Architecture

### 14 Milestones (M1-M14)

- **M1**: Foundation (core abstractions, types)
- **M2-M2.5**: Runtime (event bus, plugins, health monitoring)
- **M3-M4.5**: AI Framework & Tool Platform
- **M5-M8**: Intelligence Engines (LLM, agents, memory, orchestration)
- **M9-M11**: Domain Intelligence (video, content, editing)
- **M12-M13**: Production (rendering, publishing, 5 platforms)
- **M14**: Learning System (4 phases, feedback loop, optimization)

### Key Concepts

- **Immutable Domain Models**: Thread-safe, event sourcing ready
- **Provider Abstraction**: 30+ vendor implementations
- **Stateless Agents**: 20+ autonomous M6 agents
- **Event Sourcing**: Complete audit trail
- **DAG-Based Orchestration**: Planner → DAG → M8 → M6 → Provider
- **Capability Negotiation**: Graceful degradation

## 🛠 Development

### Using Makefile:

```bash
make help            # Show all commands
make up              # Start services
make down            # Stop services
make test            # Run tests
make lint            # Run linters
make format          # Format code
make logs            # View logs
make shell-backend   # Shell into backend
```

### Using run.sh/run.ps1:

```bash
./run.sh  # Start everything and show URLs
```

### Development Setup:

```bash
cd apps/backend
pip install -e ".[dev]"
pytest tests/
ruff check src/
mypy src/
```

## 📖 Documentation

- **[Platform README](./docs/README.md)** — Overview and features
- **[Installation Guide](./docs/INSTALLATION.md)** — Detailed setup
- **[Development Guide](./docs/DEVELOPMENT.md)** — Dev workflow
- **[Architecture](./docs/ARCHITECTURE.md)** — System design
- **[ADRs](./apps/backend/docs/architecture/adr/)** — 10 architectural decisions

## 🌐 Services

When running locally:

| Service       | URL                          | Credentials |
| ------------- | ---------------------------- | ----------- |
| Web Dashboard | http://localhost:8000        | —           |
| API Docs      | http://localhost:8000/docs   | —           |
| Backend API   | http://localhost:8000/api/v1 | —           |
| PostgreSQL    | localhost:5432               | aura/aura   |
| Redis         | localhost:6379               | —           |
| RabbitMQ Mgmt | http://localhost:15672       | guest/guest |
| Ollama        | http://localhost:11434       | —           |

## ✅ Production Ready

- **Testing**: 300+ tests, 80%+ coverage
- **Monitoring**: Metrics, health checks, structured logging
- **Security**: JWT, RBAC, audit logging, secrets management
- **Scalability**: Horizontal scaling ready
- **Documentation**: Complete architecture and operations guides

## 📦 What's Next

1. Access http://localhost:8000 to explore the platform
2. Check the [Dashboard](http://localhost:8000) to see architecture
3. Review [API Docs](http://localhost:8000/docs) for endpoints
4. Run `make test` to verify everything works
5. See [DEVELOPMENT.md](./docs/DEVELOPMENT.md) for contribution guidelines

## 📄 License

AURA is open source under the Apache 2.0 License. See [LICENSE](./LICENSE) file.

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

---

**Built with ❤️ for content creators**

For the latest updates and documentation: [aura-platform.dev](https://aura-platform.dev)
