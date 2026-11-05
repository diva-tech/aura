import { type ReactNode } from "react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui";

export interface HeroProps {
  title: string | ReactNode;
  subtitle?: string | ReactNode;
  description?: string;
  badge?: string;
  actions?: Array<{
    label: string;
    variant?: "primary" | "secondary" | "outline";
    onClick?: () => void;
  }>;
  image?: ReactNode;
  className?: string;
}

export const Hero = ({
  title,
  subtitle,
  description,
  badge,
  actions,
  image,
  className
}: HeroProps): JSX.Element => (
  <section
    className={cn(
      "relative overflow-hidden rounded-3xl border border-white/10 bg-gradient-to-br from-white/[0.08] to-white/[0.02] px-6 py-12 backdrop-blur-2xl shadow-glow-sm md:py-16 lg:py-20",
      className
    )}
  >
    {/* Gradient background elements */}
    <div className="pointer-events-none absolute inset-0 overflow-hidden">
      <div className="absolute -right-32 -top-32 h-64 w-64 rounded-full bg-cyan-400/5 blur-[100px]" />
      <div className="absolute -left-32 -bottom-32 h-64 w-64 rounded-full bg-indigo-400/5 blur-[100px]" />
    </div>

    <div className="relative space-y-6">
      {/* Badge */}
      {badge && (
        <div className="inline-flex items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-400/10 px-4 py-1.5 text-xs font-semibold text-cyan-100">
          <span className="h-1.5 w-1.5 rounded-full bg-cyan-400" />
          {badge}
        </div>
      )}

      {/* Subtitle */}
      {subtitle && typeof subtitle === "string" ? (
        <p className="text-xs uppercase tracking-[0.4em] text-slate-500 font-medium">
          {subtitle}
        </p>
      ) : (
        subtitle
      )}

      {/* Title */}
      <div>
        {typeof title === "string" ? (
          <h1 className="font-display text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight text-white">
            {title}
          </h1>
        ) : (
          <div className="font-display text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight">
            {title}
          </div>
        )}
      </div>

      {/* Description */}
      {description && (
        <p className="max-w-2xl text-base md:text-lg leading-relaxed text-slate-300/80">
          {description}
        </p>
      )}

      {/* Actions */}
      {actions && actions.length > 0 && (
        <div className="flex flex-wrap gap-3 pt-4">
          {actions.map((action, idx) => (
            <Button
              key={idx}
              variant={action.variant ?? "primary"}
              size="lg"
              onClick={action.onClick}
            >
              {action.label}
            </Button>
          ))}
        </div>
      )}

      {/* Image */}
      {image && <div className="pt-6 md:pt-8">{image}</div>}
    </div>
  </section>
);

Hero.displayName = "Hero";
