import { TerminalSquare } from "lucide-react";

import { FeaturePreview } from "@/components/ui/feature-preview";

export const LogsView = (): JSX.Element => {
  return (
    <FeaturePreview
      eyebrow="Observability"
      title="Structured operational logs with the right level of depth"
      description="Logs will expose correlation IDs, job transitions, dependency errors, and audit trails in a format that supports fast diagnosis without visual noise."
      icon={TerminalSquare}
      bullets={[
        "Correlation-aware stream inspection",
        "Per-service and per-agent filtering",
        "Audit and request traces aligned to production incidents"
      ]}
    />
  );
};
