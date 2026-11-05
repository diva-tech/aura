/**
 * Animation Presets & Utilities
 * Consistent, performant animations for premium feel
 */

import { usePrefersReducedMotion } from "./accessibility";

/**
 * Animation presets for common patterns
 */
export const animationPresets = {
  // Fade
  fadeIn: {
    initial: { opacity: 0 },
    animate: { opacity: 1 },
    exit: { opacity: 0 },
    transition: { duration: 0.3 },
  },

  // Slide from left
  slideInLeft: {
    initial: { opacity: 0, x: -20 },
    animate: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: -20 },
    transition: { duration: 0.3 },
  },

  // Slide from right
  slideInRight: {
    initial: { opacity: 0, x: 20 },
    animate: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: 20 },
    transition: { duration: 0.3 },
  },

  // Slide from top
  slideInDown: {
    initial: { opacity: 0, y: -20 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -20 },
    transition: { duration: 0.3 },
  },

  // Slide from bottom
  slideInUp: {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: 20 },
    transition: { duration: 0.3 },
  },

  // Scale
  scaleIn: {
    initial: { opacity: 0, scale: 0.95 },
    animate: { opacity: 1, scale: 1 },
    exit: { opacity: 0, scale: 0.95 },
    transition: { duration: 0.3 },
  },

  // Rotation
  rotateIn: {
    initial: { opacity: 0, rotate: -10 },
    animate: { opacity: 1, rotate: 0 },
    exit: { opacity: 0, rotate: 10 },
    transition: { duration: 0.3 },
  },

  // Stagger container
  staggerContainer: {
    initial: "hidden",
    animate: "visible",
    variants: {
      hidden: { opacity: 0 },
      visible: {
        opacity: 1,
        transition: {
          staggerChildren: 0.1,
          delayChildren: 0.2,
        },
      },
    },
  },

  // Stagger item
  staggerItem: {
    variants: {
      hidden: { opacity: 0, y: 10 },
      visible: { opacity: 1, y: 0 },
    },
  },
};

/**
 * Hook to apply animations with reduced motion support
 */
export function useAnimation(preset: any) {
  const prefersReducedMotion = usePrefersReducedMotion();

  if (prefersReducedMotion) {
    return {
      initial: preset.initial,
      animate: preset.animate,
      exit: preset.exit,
      transition: { duration: 0 },
    };
  }

  return preset;
}

/**
 * Tap animation
 */
export const tapAnimation = {
  whileTap: { scale: 0.95 },
  whileHover: { scale: 1.05 },
};

/**
 * Hover elevation
 */
export const hoverElevation = {
  whileHover: { y: -4, boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.2)" },
};

/**
 * Pulse animation
 */
export const pulseAnimation = {
  initial: { opacity: 0.6 },
  animate: {
    opacity: [0.6, 1, 0.6],
  },
  transition: {
    duration: 2,
    repeat: Infinity,
  },
};

/**
 * Bounce animation
 */
export const bounceAnimation = {
  initial: { y: 0 },
  animate: {
    y: [0, -5, 0],
  },
  transition: {
    duration: 0.6,
    repeat: Infinity,
  },
};

/**
 * Animated number counter
 */
export interface AnimatedCounterProps {
  from: number;
  to: number;
  duration?: number;
  format?: (n: number) => string;
}

export function useAnimatedCounter({
  from,
  to,
  duration = 1,
  format = (n: number) => n.toString(),
}: AnimatedCounterProps) {
  const [count, setCount] = React.useState(from);

  React.useEffect(() => {
    let start = Date.now();
    const timer = setInterval(() => {
      const elapsed = (Date.now() - start) / (duration * 1000);
      const progress = Math.min(elapsed, 1);
      const current = from + (to - from) * progress;

      setCount(Math.floor(current));

      if (progress === 1) {
        clearInterval(timer);
      }
    }, 16);

    return () => clearInterval(timer);
  }, [from, to, duration]);

  return format(count);
}

/**
 * Smooth scroll animation
 */
export function smoothScroll(target: Element, duration: number = 300) {
  const targetPosition = target.getBoundingClientRect().top + window.scrollY;
  const startPosition = window.scrollY;
  const distance = targetPosition - startPosition;
  let start: number | null = null;

  function animation(currentTime: number) {
    if (start === null) start = currentTime;
    const elapsed = currentTime - start;
    const progress = Math.min(elapsed / duration, 1);

    const ease =
      progress < 0.5
        ? 2 * progress * progress
        : -1 + (4 - 2 * progress) * progress;

    window.scrollTo(0, startPosition + distance * ease);

    if (progress < 1) {
      requestAnimationFrame(animation);
    }
  }

  requestAnimationFrame(animation);
}

/**
 * Parallax scroll effect
 */
export function useParallax(elementRef: React.RefObject<HTMLElement>) {
  const [offset, setOffset] = React.useState(0);

  React.useEffect(() => {
    const handleScroll = () => {
      if (!elementRef.current) return;

      const rect = elementRef.current.getBoundingClientRect();
      const elementCenter = rect.top + rect.height / 2;
      const windowCenter = window.innerHeight / 2;
      const distance = elementCenter - windowCenter;

      setOffset(distance * 0.5);
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, [elementRef]);

  return offset;
}

import * as React from "react";
