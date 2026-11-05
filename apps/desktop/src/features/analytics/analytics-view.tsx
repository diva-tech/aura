import { Orbit } from "lucide-react";

import { FeaturePreview } from "@/components/ui/feature-preview";

export const AnalyticsView = (): JSX.Element => {
  return (
    <FeaturePreview
      eyebrow="Signals"
      title="Cross-platform analytics with feedback loops operators can trust"
      description="Analytics will unify performance signals from every distribution surface so AURA can reason about watch time, retention, CTR, and audience behavior with discipline."
      icon={Orbit}
      bullets={[
        "Unified KPI surface across YouTube Shorts, Reels, and future channels",
        "Trend snapshots tied back to creative decisions",
        "Actionable recommendations instead of passive dashboards"
      ]}
    />
  );
};
