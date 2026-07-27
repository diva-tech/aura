import { type ReactNode, useEffect } from "react";
import { X } from "lucide-react";
import { cn } from "@/lib/utils";

export interface DialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  children: ReactNode;
  title?: string;
  description?: string;
  size?: "sm" | "md" | "lg" | "xl";
  className?: string;
}

const sizeClasses = {
  sm: "max-w-sm",
  md: "max-w-md",
  lg: "max-w-lg",
  xl: "max-w-2xl"
};

export const Dialog = ({
  open,
  onOpenChange,
  children,
  title,
  description,
  size = "md",
  className
}: DialogProps): JSX.Element | null => {
  useEffect(() => {
    if (open) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "auto";
    }

    return () => {
      document.body.style.overflow = "auto";
    };
  }, [open]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-xs animate-fade-in"
        onClick={() => onOpenChange(false)}
        role="presentation"
      />

      {/* Dialog */}
      <div
        className={cn(
          "relative w-full mx-4 rounded-3xl border border-white/10 bg-white/[0.08] p-6 backdrop-blur-2xl shadow-panel animate-scale-in",
          sizeClasses[size],
          className
        )}
      >
        {/* Header */}
        {(title || description) && (
          <div className="mb-6 space-y-1">
            {title && (
              <h2 className="font-display text-xl font-semibold text-white">
                {title}
              </h2>
            )}
            {description && (
              <p className="text-sm text-slate-400">{description}</p>
            )}
          </div>
        )}

        {/* Close button */}
        <button
          onClick={() => onOpenChange(false)}
          className="absolute right-4 top-4 rounded-xl p-1 text-slate-400 hover:bg-white/10 hover:text-white transition-all duration-200"
          aria-label="Close dialog"
        >
          <X className="h-5 w-5" />
        </button>

        {/* Content */}
        {children}
      </div>
    </div>
  );
};

Dialog.displayName = "Dialog";

export const DialogContent = ({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>): JSX.Element => (
  <div className={cn("space-y-4", className)} {...props} />
);

DialogContent.displayName = "DialogContent";

export const DialogFooter = ({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>): JSX.Element => (
  <div
    className={cn("mt-6 flex items-center justify-end gap-3", className)}
    {...props}
  />
);

DialogFooter.displayName = "DialogFooter";
