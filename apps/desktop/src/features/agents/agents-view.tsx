import { Bot } from "lucide-react";

import { FeaturePreview } from "@/components/ui/feature-preview";

export const AgentsView = (): JSX.Element => {
  return (
    <FeaturePreview
      eyebrow="Autonomy"
      title="Agent supervision designed for controlled autonomy"
      description="Editor, SEO, thumbnail, analytics, trend, and learning agents will eventually work from one governed command surface with explicit orchestration visibility."
      icon={Bot}
      bullets={[
        "Prompt packs, capability routing, and execution traces",
        "Approval checkpoints for sensitive actions",
        "Shared memory and governed task handoffs"
      ]}
    />
  );
};
