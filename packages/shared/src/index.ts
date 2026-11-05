export type HealthState = "healthy" | "degraded" | "unhealthy" | "unavailable";

export interface ComponentHealth {
  status: HealthState;
  message: string;
  latency_ms?: number | null;
}

export interface ResourceMetric {
  status: HealthState;
  total?: number | null;
  used?: number | null;
  free?: number | null;
  percent?: number | null;
}

export interface HealthPayload {
  service: string;
  environment: string;
  status: HealthState;
  backend: ComponentHealth;
  database: ComponentHealth;
  redis: ComponentHealth;
  rabbitmq: ComponentHealth;
  gpu: ResourceMetric;
  disk: ResourceMetric;
  memory: ResourceMetric;
}
