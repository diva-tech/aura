import type { LucideIcon } from "lucide-react";

import { Card } from "@/components/ui/card";

interface FeaturePreviewProps {
  eyebrow: string;
  title: string;
  description: string;
  icon: LucideIcon;
  bullets: string[];
}

export const FeaturePreview = ({
  eyebrow,
  title,
  description,
  icon: Icon,
  bullets
}: FeaturePreviewProps): JSX.Element => {
  return (
    <Card className="overflow-hidden p-0">
      <div className="relative">
        <div className="absolute inset-x-12 top-0 h-px bg-gradient-to-r from-transparent via-cyan-300/60 to-transparent" />
        <div className="absolute left-8 top-8 h-32 w-32 rounded-full bg-cyan-400/10 blur-3xl" />
        <div className="absolute right-10 top-10 h-24 w-24 rounded-full bg-indigo-400/10 blur-3xl" />
        <div className="relative grid gap-6 p-6 lg:grid-cols-[1.15fr_0.85fr] lg:p-8">
          <div className="space-y-5">
            <div className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1 text-[11px] uppercase tracking-[0.32em] text-cyan-100/75">
              <Icon className="h-3.5 w-3.5" />
              <span>{eyebrow}</span>
            </div>
            <div>
              <h3 className="font-['Space_Grotesk'] text-2xl font-semibold tracking-tight text-white lg:text-3xl">
                {title}
              </h3>
              <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-300/72">{description}</p>
            </div>
          </div>

          <div className="rounded-[28px] border border-white/10 bg-black/20 p-4 shadow-[inset_0_1px_0_rgba(255,255,255,0.05)]">
            <p className="text-xs uppercase tracking-[0.3em] text-slate-500">Planned Capabilities</p>
            <div className="mt-4 space-y-3">
              {bullets.map((bullet, index) => (
                <div
                  key={bullet}
                  className="animate-float rounded-2xl border border-white/10 bg-white/[0.04] px-4 py-3 text-sm text-slate-200/80"
                  style={{ animationDelay: `${index * 0.35}s` }}
                >
                  {bullet}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
};
