import { type ReactNode } from "react";
import { cn } from "@/lib/utils";

export interface NavItem {
  key: string;
  label: string;
  icon: ReactNode;
  badge?: string | number;
}

export interface SidebarProps {
  logo?: ReactNode;
  title?: string;
  subtitle?: string;
  navItems: NavItem[];
  activeItem?: string;
  onItemClick?: (key: string) => void;
  footer?: ReactNode;
  className?: string;
}

export const Sidebar = ({
  logo,
  title,
  subtitle,
  navItems,
  activeItem,
  onItemClick,
  footer,
  className
}: SidebarProps): JSX.Element => (
  <aside
    className={cn(
      "hidden w-[300px] shrink-0 flex-col overflow-hidden rounded-3xl border border-white/10 bg-white/[0.03] shadow-panel backdrop-blur-2xl md:flex",
      className
    )}
  >
    {/* Header */}
    {(logo || title) && (
      <div className="border-b border-white/10 px-6 pb-6 pt-7">
        {logo && <div className="mb-3">{logo}</div>}

        {title && (
          <div>
            {subtitle && (
              <p className="text-[11px] uppercase tracking-[0.45em] text-slate-500">
                {subtitle}
              </p>
            )}
            <h1 className="mt-1 font-display text-xl font-semibold text-white">
              {title}
            </h1>
          </div>
        )}
      </div>
    )}

    {/* Navigation */}
    {navItems.length > 0 && (
      <nav className="flex-1 space-y-2 px-4 py-5">
        {navItems.map((item) => {
          const isActive = item.key === activeItem;

          return (
            <button
              key={item.key}
              onClick={() => onItemClick?.(item.key)}
              type="button"
              className={cn(
                "group relative w-full rounded-2xl px-4 py-3 text-left text-sm font-medium transition-all duration-300 flex items-center justify-between",
                isActive
                  ? "bg-gradient-to-r from-cyan-500/20 to-blue-500/20 text-white border border-cyan-400/30 shadow-[0_12px_40px_rgba(34,211,238,0.15)]"
                  : "text-slate-300 hover:bg-white/5 hover:text-white"
              )}
            >
              <span className="flex items-center gap-3 flex-1">
                <span
                  className={cn(
                    "flex h-10 w-10 items-center justify-center rounded-2xl border transition-all",
                    isActive
                      ? "border-cyan-400/40 bg-cyan-400/15 text-cyan-200"
                      : "border-white/10 bg-white/5 text-slate-400 group-hover:border-white/20 group-hover:text-white"
                  )}
                >
                  {item.icon}
                </span>
                <span className="flex-1">{item.label}</span>
              </span>

              {item.badge !== undefined && (
                <span
                  className={cn(
                    "ml-2 flex items-center justify-center rounded-full text-xs font-semibold px-2 py-0.5",
                    isActive
                      ? "bg-cyan-400/30 text-cyan-100"
                      : "bg-white/10 text-slate-400 group-hover:bg-white/20"
                  )}
                >
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </nav>
    )}

    {/* Footer */}
    {footer && <div className="border-t border-white/10 px-4 py-4">{footer}</div>}
  </aside>
);

Sidebar.displayName = "Sidebar";

export const SidebarSection = ({
  title,
  children,
  className
}: {
  title?: string;
  children: ReactNode;
  className?: string;
}): JSX.Element => (
  <div className={cn("space-y-2", className)}>
    {title && (
      <p className="px-4 py-2 text-[11px] uppercase tracking-[0.35em] text-slate-500">
        {title}
      </p>
    )}
    {children}
  </div>
);

SidebarSection.displayName = "SidebarSection";
