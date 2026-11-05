import { type HTMLAttributes, type ReactNode } from "react";
import { cn } from "@/lib/utils";

export interface SectionProps extends HTMLAttributes<HTMLDivElement> {
  title?: string;
  description?: string;
  children: ReactNode;
  icon?: ReactNode;
  action?: ReactNode;
}

export const Section = ({
  title,
  description,
  children,
  icon,
  action,
  className,
  ...props
}: SectionProps): JSX.Element => (
  <section className={cn("space-y-4", className)} {...props}>
    {(title || description || action) && (
      <div className="flex items-start justify-between gap-4">
        <div className="space-y-1 flex-1">
          {title && (
            <div className="flex items-center gap-2">
              {icon && <span className="text-cyan-400">{icon}</span>}
              <h3 className="font-display text-base font-semibold text-white">
                {title}
              </h3>
            </div>
          )}
          {description && (
            <p className="text-sm text-slate-400">{description}</p>
          )}
        </div>
        {action && <div>{action}</div>}
      </div>
    )}

    <div>{children}</div>
  </section>
);

Section.displayName = "Section";
