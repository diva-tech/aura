import type { HTMLAttributes } from "react";

import { cn } from "@/lib/utils";

export const Card = ({ className, ...props }: HTMLAttributes<HTMLDivElement>): JSX.Element => {
  return (
    <div
      className={cn(
        "relative rounded-[32px] border border-white/10 bg-white/[0.045] p-5 shadow-panel backdrop-blur-2xl before:pointer-events-none before:absolute before:inset-0 before:rounded-[32px] before:border before:border-white/[0.03] before:bg-[linear-gradient(180deg,rgba(255,255,255,0.05),rgba(255,255,255,0.01))]",
        className
      )}
      {...props}
    />
  );
};
