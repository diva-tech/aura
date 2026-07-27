import "@testing-library/jest-dom";
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { App } from "../src/app/App";

describe("App", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => ({
        ok: true,
        json: async () => ({
          service: "AURA",
          environment: "test",
          status: "healthy",
          backend: { status: "healthy", message: "ok" },
          database: { status: "healthy", message: "ok" },
          redis: { status: "healthy", message: "ok" },
          rabbitmq: { status: "healthy", message: "ok" },
          gpu: { status: "healthy" },
          disk: { status: "healthy" },
          memory: { status: "healthy" }
        })
      }))
    );
  });

  it("renders the desktop dashboard shell", () => {
    render(<App />);
    expect(screen.getByText("Autonomous Unified Reel Assistant")).toBeInTheDocument();
  });
});
