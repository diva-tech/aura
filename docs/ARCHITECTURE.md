# Architecture

```mermaid
flowchart LR
    Desktop["Desktop App (Electron + React)"] --> Backend["Backend API (FastAPI)"]
    Backend --> Postgres["PostgreSQL"]
    Backend --> Redis["Redis"]
    Backend --> RabbitMQ["RabbitMQ"]
    Backend --> Ollama["Ollama / OpenAI-compatible APIs"]
    Backend --> Storage["Storage Buckets / Local Media Storage"]

    subgraph Agents
      Editor["Editor Agent"]
      SEO["SEO Agent"]
      Thumbnail["Thumbnail Agent"]
      Analytics["Analytics Agent"]
      Trend["Trend Agent"]
      Learning["Learning Agent"]
    end

    subgraph Services
      Video["Video Service"]
      ThumbSvc["Thumbnail Service"]
      UploadSvc["Uploader Service"]
      AnalyticsSvc["Analytics Service"]
    end

    Backend --> Agents
    Backend --> Services
```

## Notes

- The current scaffold focuses on platform foundation, not business workflows.
- The backend owns orchestration, health, configuration, and shared integration boundaries.
- Services and agents are intentionally separated to preserve future deployment flexibility.
- Long-lived dependency clients are composed during application startup and reused across requests.
- The desktop shell consumes backend APIs through isolated client modules rather than direct feature-level fetch calls.
