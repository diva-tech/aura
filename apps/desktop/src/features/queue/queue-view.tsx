import { Waves } from "lucide-react";

import { FeaturePreview } from "@/components/ui/feature-preview";

export const QueueView = (): JSX.Element => {
  return (
    <FeaturePreview
      eyebrow="Processing"
      title="Queue orchestration with visible throughput and retry control"
      description="This lane is reserved for priority-aware workloads, safe retries, worker visibility, and time-based orchestration across the media pipeline."
      icon={Waves}
      bullets={[
        "Priority lanes for urgent and scheduled jobs",
        "Worker occupancy, retries, and dead-letter visibility",
        "Latency and backlog telemetry for operator decision-making"
      ]}
    />
  );
};
