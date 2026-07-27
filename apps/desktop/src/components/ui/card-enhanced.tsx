import { type HTMLAttributes } from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const cardVariants = cva(
  "relative rounded-3xl border transition-all duration-300",
  {
    variants: {
      variant: {
        glass:
          "border-white/10 bg-white/[0.05] backdrop-blur-xl hover:bg-white/[0.08] hover:border-white/20 hover:shadow-glow-sm",
        "glass-dark":
          "border-white/5 bg-black/30 backdrop-blur-2xl hover:bg-black/40 hover:border-white/10",
        gradient:
          "border-white/10 bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-xl hover:from-white/15 hover:to-white/10",
        solid: "border-white/20 bg-white/10 hover:bg-white/15 hover:border-white/30",
        outline:
          "border-white/20 bg-transparent hover:bg-white/5 hover:border-white/30"
      }
    },
    defaultVariants: {
      variant: "glass"
    }
  }
);

export interface CardProps
  extends HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof cardVariants> {}

export const Card = ({
  className,
  variant,
  ...props
}: CardProps): JSX.Element => (
  <div className={cn(cardVariants({ variant, className }))} {...props} />
);

Card.displayName = "Card";

export const CardContent = ({
  className,
  ...props
}: HTMLAttributes<HTMLDivElement>): JSX.Element => (
  <div className={cn("p-6", className)} {...props} />
);

CardContent.displayName = "CardContent";

export const CardHeader = ({
  className,
  ...props
}: HTMLAttributes<HTMLDivElement>): JSX.Element => (
  <div className={cn("space-y-2", className)} {...props} />
);

CardHeader.displayName = "CardHeader";

export const CardTitle = ({
  className,
  ...props
}: HTMLAttributes<HTMLHeadingElement>): JSX.Element => (
  <h3
    className={cn("font-display text-lg font-semibold text-white", className)}
    {...props}
  />
);

CardTitle.displayName = "CardTitle";

export const CardDescription = ({
  className,
  ...props
}: HTMLAttributes<HTMLParagraphElement>): JSX.Element => (
  <p className={cn("text-sm text-slate-400", className)} {...props} />
);

CardDescription.displayName = "CardDescription";
