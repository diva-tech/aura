import { ArrowUpRight, BrainCircuit, Layers3, ScanSearch, Sparkles } from "lucide-react";

import { Card } from "@/components/ui/card";
import { useHealthQuery } from "@/features/dashboard/use-health-query";

export const DashboardView = (): JSX.Element => {
  const { data, isLoading, isError } = useHealthQuery();
  const metrics = [
    { title: "Service", value: data?.service ?? "AURA", description: "Primary API boundary" },
    {
      title: "Status",
      value: isLoading ? "Checking" : data?.status ?? "Unknown",
      description: "Overall runtime health"
    },
    {
      title: "Environment",
      value: data?.environment ?? "development",
      description: "Current deployment mode"
    },
    {
      title: "Database",
      value: data?.database.status ?? "Pending",
      description: "PostgreSQL readiness"
    },
    {
      title: "Redis",
      value: data?.redis.status ?? "Pending",
      description: "Cache and coordination"
    },
    {
      title: "RabbitMQ",
      value: data?.rabbitmq.status ?? "Pending",
      description: "Async delivery backbone"
    }
  ];
  const operationalLanes = [
    {
      title: "Scene Intelligence",
      detail: "Detect hooks, cuts, retention pivots, and narrative transitions."
    },
    {
      title: "Distribution Engine",
      detail: "Prepare launch-ready shorts, reels, thumbnails, and metadata variants."
    },
    {
      title: "Learning Loop",
      detail: "Turn watch-time and click-through feedback into system-level improvements."
    }
  ];

  return (
    <section className="grid gap-5">
      <Card className="overflow-hidden p-0">
        <div className="relative grid gap-8 px-6 py-6 lg:grid-cols-[1.25fr_0.75fr] lg:px-8 lg:py-8">
          <div className="space-y-6">
            <div className="inline-flex items-center gap-2 rounded-full border border-cyan-300/15 bg-cyan-400/10 px-3 py-1 text-[11px] uppercase tracking-[0.3em] text-cyan-100/75">
              <Sparkles className="h-3.5 w-3.5" />
              <span>Realtime System View</span>
            </div>
            <div>
              <h3 className="max-w-3xl font-['Space_Grotesk'] text-3xl font-semibold tracking-tight text-white lg:text-4xl">
                A calm, intelligent cockpit for high-output content operations
              </h3>
              <p className="mt-4 max-w-2xl text-sm leading-7 text-slate-300/70">
                AURA gives operators one premium surface for orchestration, observability, and
                creative execution across every AI-assisted publishing lane.
              </p>
            </div>
            <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
              {metrics.map((metric, index) => (
                <Metric
                  key={metric.title}
                  title={metric.title}
                  value={metric.value}
                  description={metric.description}
                  delay={index}
                />
              ))}
            </div>
          </div>

          <div className="rounded-[30px] border border-white/10 bg-black/20 p-5 shadow-[inset_0_1px_0_rgba(255,255,255,0.04)]">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs uppercase tracking-[0.3em] text-slate-500">Operational Lanes</p>
                <p className="mt-2 text-lg font-semibold text-white">High-signal execution map</p>
              </div>
              <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-2 text-slate-300">
                <Layers3 className="h-4 w-4" />
              </div>
            </div>
            <div className="mt-5 space-y-3">
              {operationalLanes.map((lane, index) => (
                <div
                  key={lane.title}
                  className="animate-fade-up rounded-2xl border border-white/10 bg-white/[0.03] p-4"
                  style={{ animationDelay: `${index * 0.08}s` }}
                >
                  <div className="flex items-center justify-between">
                    <p className="font-medium text-white">{lane.title}</p>
                    <ArrowUpRight className="h-4 w-4 text-slate-500" />
                  </div>
                  <p className="mt-2 text-sm leading-6 text-slate-400">{lane.detail}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
        {isError ? (
          <div className="mx-6 mb-6 rounded-2xl border border-red-400/20 bg-red-500/10 p-4 text-sm text-red-200 lg:mx-8">
            Backend health could not be reached. The desktop shell is working, but the API is not responding yet.
          </div>
        ) : null}
      </Card>

      <div className="grid gap-5 xl:grid-cols-[1.1fr_0.9fr]">
        <Card className="p-6 lg:p-7">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-cyan-300/15 bg-cyan-400/10 text-cyan-100">
              <ScanSearch className="h-5 w-5" />
            </div>
            <div>
              <p className="text-xs uppercase tracking-[0.3em] text-slate-500">Roadmap Modules</p>
              <h4 className="mt-2 text-xl font-semibold text-white">Execution surface already shaped for scale</h4>
            </div>
          </div>
          <div className="mt-6 grid gap-4 md:grid-cols-2">
            {[
              "Automated clip selection",
              "Multi-agent SEO generation",
              "Thumbnail experimentation",
              "Self-optimizing analytics loops"
            ].map((item, index) => (
              <div
                key={item}
                className="animate-fade-up rounded-[26px] border border-white/10 bg-white/[0.03] p-5"
                style={{ animationDelay: `${index * 0.06}s` }}
              >
                <p className="font-medium text-white">{item}</p>
                <p className="mt-2 text-sm leading-6 text-slate-400">
                  Reserved for enterprise-grade orchestration, telemetry, and rollout governance.
                </p>
              </div>
            ))}
          </div>
        </Card>

        <Card className="p-6 lg:p-7">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-violet-300/15 bg-violet-400/10 text-violet-100">
              <BrainCircuit className="h-5 w-5" />
            </div>
            <div>
              <p className="text-xs uppercase tracking-[0.3em] text-slate-500">Design Intent</p>
              <h4 className="mt-2 text-xl font-semibold text-white">Premium product language</h4>
            </div>
          </div>
          <div className="mt-6 space-y-3">
            {[
              "Glassmorphism surfaces with low-noise borders",
              "High-density information hierarchy without clutter",
              "Subtle motion designed around clarity, not novelty"
            ].map((item, index) => (
              <div
                key={item}
                className="animate-float rounded-2xl border border-white/10 bg-black/20 px-4 py-4 text-sm text-slate-200/80"
                style={{ animationDelay: `${index * 0.35}s` }}
              >
                {item}
              </div>
            ))}
          </div>
        </Card>
      </div>
    </section>
  );
};

const Metric = ({
  title,
  value,
  description,
  delay
}: {
  title: string;
  value: string;
  description: string;
  delay: number;
}): JSX.Element => {
  return (
    <div
      className="animate-fade-up rounded-[28px] border border-white/10 bg-black/20 p-4"
      style={{ animationDelay: `${delay * 0.07}s` }}
    >
      <p className="text-[11px] uppercase tracking-[0.28em] text-slate-500">{title}</p>
      <p className="mt-3 font-['Space_Grotesk'] text-2xl font-semibold text-white">{value}</p>
      <p className="mt-2 text-sm leading-6 text-slate-400">{description}</p>
    </div>
  );
};
