import { env } from "@/config/env";

interface RequestOptions extends Omit<RequestInit, "signal"> {
  path: string;
  timeoutMs?: number;
}

export const requestJson = async <T>({
  path,
  timeoutMs = env.requestTimeoutMs,
  headers,
  ...init
}: RequestOptions): Promise<T> => {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(`${env.apiBaseUrl}${path}`, {
      ...init,
      headers: {
        Accept: "application/json",
        ...headers
      },
      signal: controller.signal
    });

    if (!response.ok) {
      throw new Error(`Request failed with status ${response.status}`);
    }

    return (await response.json()) as T;
  } finally {
    window.clearTimeout(timeout);
  }
};
