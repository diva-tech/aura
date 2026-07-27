import { type HTMLAttributes } from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-full border font-medium text-xs px-3 py-1.5 transition-all duration-200",
  {
    variants: {
      variant: {
        default:
          "border-white/20 bg-white/5 text-white hover:bg-white/10 hover:border-white/30",
        primary:
          "border-cyan-400/20 bg-cyan-400/10 text-cyan-100 hover:bg-cyan-400/20 hover:border-cyan-400/30",
        secondary:
          "border-indigo-400/20 bg-indigo-400/10 text-indigo-100 hover:bg-indigo-400/20 hover:border-indigo-400/30",
        success:
          "border-green-400/20 bg-green-400/10 text-green-100 hover:bg-green-400/20 hover:border-green-400/30",
        warning:
          "border-amber-400/20 bg-amber-400/10 text-amber-100 hover:bg-amber-400/20 hover:border-amber-400/30",
        error:
          "border-red-400/20 bg-red-400/10 text-red-100 hover:bg-red-400/20 hover:border-red-400/30",
        outline:
          "border-white/20 text-white bg-transparent hover:border-white/40 hover:bg-white/5"
      },
      size: {
        sm: "text-xs px-2 py-1",
        md: "text-sm px-3 py-1.5",
        lg: "text-base px-4 py-2"
      }
    },
    defaultVariants: {
      variant: "default",
      size: "md"
    }
  }
);

export interface BadgeProps
  extends HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

export const Badge = ({
  className,
  variant,
  size,
  ...props
}: BadgeProps): JSX.Element => (
  <div className={cn(badgeVariants({ variant, size, className }))} {...props} />
);

Badge.displayName = "Badge";
