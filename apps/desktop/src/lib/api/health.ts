import type { HealthPayload } from "@aura/shared";

import { requestJson } from "@/lib/api/http-client";

export const fetchHealth = async (): Promise<HealthPayload> =>
  requestJson<HealthPayload>({
    path: "/api/v1/health"
  });
