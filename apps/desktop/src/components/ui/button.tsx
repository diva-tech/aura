import { type HTMLAttributes, type ReactNode, forwardRef } from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "relative inline-flex items-center justify-center whitespace-nowrap rounded-2xl font-medium transition-all duration-200 ease-out focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 focus-visible:ring-offset-background disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        primary:
          "bg-gradient-to-r from-cyan-500 to-blue-500 text-white hover:shadow-glow hover:-translate-y-0.5 active:-translate-y-1",
        secondary:
          "bg-white/10 border border-white/20 text-white hover:bg-white/15 hover:border-white/30 hover:shadow-glow-sm",
        outline:
          "border border-white/20 text-foreground hover:bg-white/5 hover:border-white/30",
        ghost: "text-foreground hover:bg-white/5",
        accent:
          "bg-gradient-to-r from-indigo-500 to-purple-500 text-white hover:shadow-glow hover:-translate-y-0.5 active:-translate-y-1",
        danger: "bg-red-500/20 border border-red-500/30 text-red-200 hover:bg-red-500/30 hover:border-red-500/50"
      },
      size: {
        sm: "h-9 px-3 text-sm",
        md: "h-10 px-4 text-base",
        lg: "h-12 px-6 text-base",
        xl: "h-14 px-8 text-lg",
        icon: "h-10 w-10"
      }
    },
    defaultVariants: {
      variant: "primary",
      size: "md"
    }
  }
);

export interface ButtonProps
  extends HTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
  loading?: boolean;
  icon?: ReactNode;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant,
      size,
      loading = false,
      disabled = false,
      icon,
      children,
      ...props
    },
    ref
  ) => (
    <button
      ref={ref}
      className={cn(buttonVariants({ variant, size, className }))}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <div className="mr-2 inline-flex h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
      ) : icon ? (
        <span className="mr-2 inline-flex">{icon}</span>
      ) : null}
      {children}
    </button>
  )
);

Button.displayName = "Button";
