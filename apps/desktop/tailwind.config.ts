import type { Config } from "tailwindcss";

export default {
  darkMode: ["class"],
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        card: "hsl(var(--card))",
        border: "hsl(var(--border))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          light: "hsl(var(--primary-light))",
          dark: "hsl(var(--primary-dark))"
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          light: "hsl(var(--accent-light))",
          dark: "hsl(var(--accent-dark))"
        },
        muted: "hsl(var(--muted))",
        success: "hsl(var(--success))",
        warning: "hsl(var(--warning))",
        error: "hsl(var(--error))"
      },
      fontFamily: {
        sans: ["'Inter'", "system-ui", "sans-serif"],
        display: ["'Space Grotesk'", "system-ui", "sans-serif"]
      },
      boxShadow: {
        panel: "0 20px 60px rgba(0, 0, 0, 0.35)",
        glow: "0 0 30px rgba(34, 211, 238, 0.15)",
        "glow-sm": "0 0 15px rgba(34, 211, 238, 0.1)",
        "glow-lg": "0 0 50px rgba(34, 211, 238, 0.2)"
      },
      backdropBlur: {
        xs: "2px"
      },
      animation: {
        "fade-up": "fade-up 0.6s cubic-bezier(0.16, 1, 0.3, 1) both",
        "fade-in": "fade-in 0.6s cubic-bezier(0.16, 1, 0.3, 1) both",
        "blur-in": "blur-in 0.7s cubic-bezier(0.16, 1, 0.3, 1) both",
        "scale-in": "scale-in 0.5s cubic-bezier(0.16, 1, 0.3, 1) both",
        "slide-in-right": "slide-in-right 0.5s cubic-bezier(0.16, 1, 0.3, 1) both",
        "slide-in-left": "slide-in-left 0.5s cubic-bezier(0.16, 1, 0.3, 1) both",
        "float": "float 8s ease-in-out infinite",
        "glow": "glow 3s ease-in-out infinite",
        "pulse-ring": "pulse-ring 2s ease-out infinite",
        "shimmer": "shimmer 2s infinite"
      },
      keyframes: {
        "fade-up": {
          "0%": { opacity: "0", transform: "translateY(20px)" },
          "100%": { opacity: "1", transform: "translateY(0)" }
        },
        "fade-in": {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" }
        },
        "blur-in": {
          "0%": { opacity: "0", filter: "blur(8px)" },
          "100%": { opacity: "1", filter: "blur(0)" }
        },
        "scale-in": {
          "0%": { opacity: "0", transform: "scale(0.95)" },
          "100%": { opacity: "1", transform: "scale(1)" }
        },
        "slide-in-right": {
          "0%": { opacity: "0", transform: "translateX(20px)" },
          "100%": { opacity: "1", transform: "translateX(0)" }
        },
        "slide-in-left": {
          "0%": { opacity: "0", transform: "translateX(-20px)" },
          "100%": { opacity: "1", transform: "translateX(0)" }
        },
        "float": {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-6px)" }
        },
        "glow": {
          "0%, 100%": {
            opacity: "0.5",
            filter: "drop-shadow(0 0 8px rgba(34, 211, 238, 0.3))"
          },
          "50%": {
            opacity: "1",
            filter: "drop-shadow(0 0 16px rgba(34, 211, 238, 0.6))"
          }
        },
        "pulse-ring": {
          "0%": { transform: "scale(1)", opacity: "1" },
          "100%": { transform: "scale(1.5)", opacity: "0" }
        },
        "shimmer": {
          "0%": { "background-position": "-1000px 0" },
          "100%": { "background-position": "1000px 0" }
        }
      }
    }
  },
  plugins: []
} satisfies Config;
