"use client";

import { useState } from "react";
import { AuraCopilot } from "@/components/copilot/AuraCopilot";
import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "@/lib/api/client";

export default function ProjectsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [copilotOpen, setCopilotOpen] = useState(false);

  return (
    <QueryClientProvider client={queryClient}>
      <div className="relative w-full h-screen bg-slate-950">
        {children}
        <AuraCopilot
          projectId="current"
          isOpen={copilotOpen}
          onToggle={() => setCopilotOpen(!copilotOpen)}
        />
      </div>
    </QueryClientProvider>
  );
}
