const DEFAULT_API_BASE_URL = "http://localhost:8000";
const DEFAULT_REQUEST_TIMEOUT_MS = 5000;

export const env = {
  apiBaseUrl: String(import.meta.env.VITE_API_BASE_URL ?? DEFAULT_API_BASE_URL),
  requestTimeoutMs: Number(import.meta.env.VITE_REQUEST_TIMEOUT_MS ?? DEFAULT_REQUEST_TIMEOUT_MS)
};
