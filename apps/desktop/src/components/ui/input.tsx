import { type InputHTMLAttributes, forwardRef } from "react";
import { cn } from "@/lib/utils";

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  icon?: React.ReactNode;
  iconPosition?: "left" | "right";
  error?: boolean;
  helperText?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      className,
      icon,
      iconPosition = "left",
      error = false,
      helperText,
      type = "text",
      ...props
    },
    ref
  ) => (
    <div className="w-full">
      <div
        className={cn(
          "relative flex items-center rounded-2xl border bg-white/5 backdrop-blur transition-all duration-200",
          error
            ? "border-red-400/50 focus-within:border-red-400 focus-within:bg-red-400/5"
            : "border-white/10 focus-within:border-cyan-400/50 focus-within:bg-white/10",
          icon && iconPosition === "left" && "pl-3",
          icon && iconPosition === "right" && "pr-3"
        )}
      >
        {icon && iconPosition === "left" && (
          <span className="flex h-10 items-center text-slate-400">{icon}</span>
        )}

        <input
          ref={ref}
          type={type}
          className={cn(
            "h-10 w-full flex-1 bg-transparent px-4 py-2 text-sm text-white placeholder-slate-500 outline-none transition-colors duration-200",
            className
          )}
          {...props}
        />

        {icon && iconPosition === "right" && (
          <span className="flex h-10 items-center text-slate-400">{icon}</span>
        )}
      </div>

      {helperText && (
        <p
          className={cn(
            "mt-2 text-xs",
            error ? "text-red-400/70" : "text-slate-400"
          )}
        >
          {helperText}
        </p>
      )}
    </div>
  )
);

Input.displayName = "Input";
