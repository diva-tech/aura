import type { LucideIcon } from "lucide-react";
import {
  BrainCircuit,
  ChartNoAxesCombined,
  Clapperboard,
  FileUp,
  LayoutDashboard,
  Logs,
  Palette,
  Settings
} from "lucide-react";

import { AgentsView } from "@/features/agents/agents-view";
import { AnalyticsView } from "@/features/analytics/analytics-view";
import { DashboardView } from "@/features/dashboard/dashboard-view";
import { LogsView } from "@/features/logs/logs-view";
import { QueueView } from "@/features/queue/queue-view";
import { SettingsView } from "@/features/settings/settings-view";
import { UploadsView } from "@/features/uploads/uploads-view";
import { ShowcaseView } from "@/features/showcase/showcase-view";

export type NavigationKey =
  | "dashboard"
  | "uploads"
  | "queue"
  | "analytics"
  | "agents"
  | "settings"
  | "logs"
  | "showcase";

export interface NavigationItem {
  key: NavigationKey;
  label: string;
  icon: LucideIcon;
}

export const navigationItems: NavigationItem[] = [
  { key: "dashboard", label: "Dashboard", icon: LayoutDashboard },
  { key: "uploads", label: "Uploads", icon: FileUp },
  { key: "queue", label: "Queue", icon: Clapperboard },
  { key: "analytics", label: "Analytics", icon: ChartNoAxesCombined },
  { key: "agents", label: "AI Agents", icon: BrainCircuit },
  { key: "showcase", label: "Components", icon: Palette },
  { key: "settings", label: "Settings", icon: Settings },
  { key: "logs", label: "Logs", icon: Logs }
];

export const navigationViews: Record<NavigationKey, JSX.Element> = {
  dashboard: <DashboardView />,
  uploads: <UploadsView />,
  queue: <QueueView />,
  analytics: <AnalyticsView />,
  agents: <AgentsView />,
  showcase: <ShowcaseView />,
  settings: <SettingsView />,
  logs: <LogsView />
};
