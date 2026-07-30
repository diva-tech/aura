/**
 * Accessibility Utilities
 * WCAG 2.1 AA compliance helpers
 */

import { useEffect, useState } from "react";

/**
 * Detect reduced motion preference
 */
export function usePrefersReducedMotion(): boolean {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
    setPrefersReducedMotion(mediaQuery.matches);

    const handleChange = (e: MediaQueryListEvent) => {
      setPrefersReducedMotion(e.matches);
    };

    mediaQuery.addEventListener("change", handleChange);
    return () => mediaQuery.removeEventListener("change", handleChange);
  }, []);

  return prefersReducedMotion;
}

/**
 * Focus management utilities
 */
export function focusElement(element: HTMLElement | null) {
  if (element) {
    element.focus();
  }
}

export function focusFirst(selector: string) {
  const element = document.querySelector(selector) as HTMLElement;
  focusElement(element);
}

export function trapFocus(containerRef: React.RefObject<HTMLDivElement>) {
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const focusableElements = container.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );

    if (focusableElements.length === 0) return;

    const firstElement = focusableElements[0] as HTMLElement;
    const lastElement = focusableElements[
      focusableElements.length - 1
    ] as HTMLElement;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key !== "Tab") return;

      if (e.shiftKey) {
        if (document.activeElement === firstElement) {
          e.preventDefault();
          lastElement.focus();
        }
      } else {
        if (document.activeElement === lastElement) {
          e.preventDefault();
          firstElement.focus();
        }
      }
    };

    container.addEventListener("keydown", handleKeyDown);
    return () => container.removeEventListener("keydown", handleKeyDown);
  }, [containerRef]);
}

/**
 * Announce to screen readers
 */
export function announce(
  message: string,
  priority: "polite" | "assertive" = "polite"
) {
  const div = document.createElement("div");
  div.setAttribute("role", "status");
  div.setAttribute("aria-live", priority);
  div.setAttribute("aria-atomic", "true");
  div.className = "sr-only";
  div.textContent = message;

  document.body.appendChild(div);

  setTimeout(() => {
    document.body.removeChild(div);
  }, 1000);
}

/**
 * Color contrast checking (WCAG AA: 4.5:1 for normal text)
 */
export function getContrastRatio(
  foreground: string,
  background: string
): number {
  const getLuminance = (color: string): number => {
    const rgb = parseInt(color.slice(1), 16);
    const r = (rgb >> 16) & 255;
    const g = (rgb >> 8) & 255;
    const b = rgb & 255;

    const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;

    return luminance <= 0.03928
      ? luminance / 12.92
      : Math.pow((luminance + 0.055) / 1.055, 2.4);
  };

  const l1 = getLuminance(foreground);
  const l2 = getLuminance(background);

  const lighter = Math.max(l1, l2);
  const darker = Math.min(l1, l2);

  return (lighter + 0.05) / (darker + 0.05);
}

/**
 * Skip to content link
 * See components/global/SkipToContent.tsx for implementation
 */

/**
 * Heading hierarchy checker
 */
export function validateHeadingHierarchy(): string[] {
  const headings = document.querySelectorAll("h1, h2, h3, h4, h5, h6");
  const issues: string[] = [];
  let lastLevel = 0;

  headings.forEach((heading, idx) => {
    const level = parseInt(heading.tagName[1]);

    if (idx === 0 && level !== 1) {
      issues.push("Page should start with H1");
    }

    if (level - lastLevel > 1) {
      issues.push(`Heading hierarchy skipped from H${lastLevel} to H${level}`);
    }

    lastLevel = level;
  });

  return issues;
}

/**
 * ARIA label utilities
 */
export function useAriaLabel(label: string) {
  return { "aria-label": label };
}

export function useAriaDescribedBy(id: string) {
  return { "aria-describedby": id };
}

export function useAriaLabelledBy(id: string) {
  return { "aria-labelledby": id };
}

/**
 * Semantic HTML helpers
 */
export const ARIA = {
  button: { role: "button", tabIndex: 0 },
  link: { role: "link", tabIndex: 0 },
  alert: { role: "alert" },
  status: { role: "status", "aria-live": "polite" },
  progressbar: {
    role: "progressbar",
    "aria-valuenow": 0,
    "aria-valuemin": 0,
    "aria-valuemax": 100,
  },
};
