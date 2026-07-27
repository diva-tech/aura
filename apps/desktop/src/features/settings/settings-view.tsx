import { SlidersHorizontal } from "lucide-react";

import { FeaturePreview } from "@/components/ui/feature-preview";

export const SettingsView = (): JSX.Element => {
  return (
    <FeaturePreview
      eyebrow="Control"
      title="Configuration surfaces for providers, environments, and policy"
      description="Settings is reserved for secure provider onboarding, deployment-aware runtime profiles, and operator-level controls that should feel precise rather than overwhelming."
      icon={SlidersHorizontal}
      bullets={[
        "Provider credentials and endpoint policy separation",
        "Environment-specific execution profiles",
        "Operational toggles for governance and observability"
      ]}
    />
  );
};
