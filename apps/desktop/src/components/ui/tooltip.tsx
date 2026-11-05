import { type HTMLAttributes, type ReactNode, useState } from "react";
import { cn } from "@/lib/utils";

export interface TooltipProps extends HTMLAttributes<HTMLDivElement> {
  content: string | ReactNode;
  side?: "top" | "bottom" | "left" | "right";
  delay?: number;
  children: ReactNode;
}

export const Tooltip = ({
  content,
  side = "top",
  delay = 200,
  children,
  className,
  ...props
}: TooltipProps): JSX.Element => {
  const [isVisible, setIsVisible] = useState(false);
  const [timeoutId, setTimeoutId] = useState<NodeJS.Timeout | null>(null);

  const handleMouseEnter = (): void => {
    const id = setTimeout(() => setIsVisible(true), delay);
    setTimeoutId(id);
  };

  const handleMouseLeave = (): void => {
    if (timeoutId) clearTimeout(timeoutId);
    setIsVisible(false);
  };

  const positionClasses = {
    top: "bottom-full left-1/2 -translate-x-1/2 mb-2",
    bottom: "top-full left-1/2 -translate-x-1/2 mt-2",
    left: "right-full top-1/2 -translate-y-1/2 mr-2",
    right: "left-full top-1/2 -translate-y-1/2 ml-2"
  };

  return (
    <div
      className="relative inline-block"
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      {...props}
    >
      {children}

      {isVisible && (
        <div
          className={cn(
            "absolute z-50 whitespace-nowrap rounded-xl border border-white/10 bg-slate-950/95 px-3 py-2 text-xs text-slate-200 backdrop-blur-xl shadow-lg animate-fade-in",
            positionClasses[side],
            className
          )}
        >
          {content}

          <div
            className={cn(
              "absolute w-2 h-2 bg-slate-950/95 border border-white/10 rotate-45",
              side === "top" && "top-full left-1/2 -translate-x-1/2 -mt-1",
              side === "bottom" && "bottom-full left-1/2 -translate-x-1/2 mb-0",
              side === "left" && "left-full top-1/2 -translate-y-1/2 -ml-1",
              side === "right" && "right-full top-1/2 -translate-y-1/2 mr-0"
            )}
          />
        </div>
      )}
    </div>
  );
};

Tooltip.displayName = "Tooltip";
