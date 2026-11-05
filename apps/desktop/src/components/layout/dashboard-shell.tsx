import { startTransition, useState } from "react";
import { BellRing, Search, Sparkles, Workflow } from "lucide-react";

import { cn } from "@/lib/utils";
import { Sidebar } from "./sidebar";
import { Badge } from "@/components/ui/badge";
import {
  type NavigationKey,
  navigationItems,
  navigationViews
} from "@/features/navigation/navigation";

export const DashboardShell = (): JSX.Element => {
  const [activeView, setActiveView] = useState<NavigationKey>("dashboard");

  const handleNavigate = (key: string): void => {
    startTransition(() => {
      setActiveView(key as NavigationKey);
    });
  };

  return (
    <div className="glass-grid min-h-screen text-foreground">
      {/* Animated background gradients */}
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute left-[8%] top-24 h-96 w-96 rounded-full bg-cyan-400/8 blur-[140px] animate-pulse" />
        <div className="absolute right-[10%] top-16 h-96 w-96 rounded-full bg-indigo-500/8 blur-[150px] animate-pulse" />
        <div className="absolute bottom-10 left-1/2 h-96 w-96 -translate-x-1/2 rounded-full bg-sky-400/8 blur-[150px] animate-pulse" />
      </div>

      <div className="relative mx-auto flex min-h-screen max-w-[1920px] gap-6 px-3 py-3 sm:px-4 lg:px-6">
        {/* Sidebar */}
        <Sidebar
          logo={
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-cyan-400/20 bg-gradient-to-br from-cyan-400/20 to-blue-400/10 text-cyan-200 shadow-glow-sm">
              <Sparkles className="h-5 w-5" />
            </div>
          }
          title="Autonomous Studio"
          subtitle="AURA OS"
          navItems={navigationItems.map((item) => ({
            key: item.key,
            label: item.label,
            icon: <item.icon className="h-4 w-4" />,
            badge: item.badge
          }))}
          activeItem={activeView}
          onItemClick={handleNavigate}
          footer={
            <div className="space-y-3">
              <div className="rounded-2xl border border-cyan-400/20 bg-gradient-to-br from-cyan-400/10 to-blue-400/5 p-4 backdrop-blur">
                <div className="flex items-center gap-3 mb-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-cyan-400/20 text-cyan-200">
                    <Workflow className="h-4 w-4" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-white">Command Graph</p>
                    <p className="text-xs text-slate-400">Orchestration online</p>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-2 text-sm">
                  <StatusMetric label="Pipelines" value="24" />
                  <StatusMetric label="Models" value="6" />
                </div>
              </div>

              <button className="w-full rounded-xl border border-white/10 bg-white/5 p-2.5 text-slate-400 hover:bg-white/10 hover:text-white transition-all duration-200 flex items-center justify-center gap-2">
                <BellRing className="h-4 w-4" />
                <span className="text-xs">Notifications</span>
              </button>
            </div>
          }
        />

        <main className="flex-1 flex flex-col animate-fade-up">
          {/* Header */}
          <header className="relative mb-6 overflow-hidden rounded-3xl border border-white/10 bg-gradient-to-br from-white/[0.08] to-white/[0.02] px-6 py-8 backdrop-blur-2xl shadow-glow-sm">
            <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-cyan-300/50 to-transparent" />

            <div className="relative space-y-6">
              <div>
                <p className="text-xs uppercase tracking-[0.4em] text-slate-500 font-medium">
                  Control Center
                </p>
                <h1 className="mt-3 font-display text-3xl md:text-4xl font-semibold text-white tracking-tight">
                  <span className="gradient-text">Autonomous Studio</span>
                </h1>
                <p className="mt-4 max-w-2xl text-sm leading-7 text-slate-300/70">
                  Professional creative operations powered by AI. Inspired by Linear, Vercel, Raycast,
                  Apple, and OpenAI.
                </p>
              </div>

              {/* Status badges */}
              <div className="flex flex-wrap gap-3 pt-2">
                <StatusChip label="Backend" value="Ready" tone="cyan" />
                <StatusChip label="Queue" value="Idle" tone="slate" />
                <StatusChip label="Agents" value="6 Online" tone="violet" />
              </div>
            </div>
          </header>

          {/* Mobile nav */}
          <div className="mb-6 flex gap-2 overflow-x-auto pb-2 md:hidden">
            {navigationItems.map((item) => (
              <button
                key={item.key}
                onClick={() => handleNavigate(item.key)}
                className={cn(
                  "flex items-center gap-2 rounded-full px-4 py-2 text-sm whitespace-nowrap font-medium transition-all duration-300",
                  item.key === activeView
                    ? "bg-gradient-to-r from-cyan-500/30 to-blue-500/30 border border-cyan-400/40 text-cyan-100 shadow-glow-sm"
                    : "border border-white/10 bg-white/5 text-slate-300 hover:bg-white/10"
                )}
              >
                <item.icon className="h-4 w-4" />
                {item.label}
              </button>
            ))}
          </div>

          {/* Content */}
          <div className="flex-1 animate-fade-up">
            {navigationViews[activeView]}
          </div>
        </main>
      </div>
    </div>
  );
};

const StatusChip = ({
  label,
  value,
  tone
}: {
  label: string;
  value: string;
  tone: "cyan" | "slate" | "violet";
}): JSX.Element => {
  const toneClasses = {
    cyan: "from-cyan-500/20 to-blue-500/10 border-cyan-400/30 text-cyan-100",
    slate: "from-white/10 to-white/5 border-white/20 text-slate-100",
    violet: "from-violet-500/20 to-indigo-500/10 border-violet-400/30 text-violet-100"
  };

  const [bgFrom, bgTo, borderColor, textColor] = toneClasses.split(" ");

  return (
    <div
      className={cn(
        "rounded-2xl border backdrop-blur px-4 py-3 transition-all duration-300 hover:shadow-glow-sm",
        `bg-gradient-to-r ${bgFrom} ${bgTo} ${borderColor} ${textColor}`
      )}
    >
      <p className="text-[10px] uppercase tracking-[0.3em] text-current/70 font-semibold">
        {label}
      </p>
      <p className="mt-1 font-display text-base font-semibold text-current">{value}</p>
    </div>
  );
};

const StatusMetric = ({ label, value }: { label: string; value: string }): JSX.Element => {
  return (
    <div className="rounded-xl border border-white/10 bg-white/5 px-3 py-2 backdrop-blur">
      <p className="text-[10px] uppercase tracking-[0.25em] text-slate-400 font-medium">
        {label}
      </p>
      <p className="mt-1 font-display text-base font-semibold text-white">{value}</p>
    </div>
  );
};
