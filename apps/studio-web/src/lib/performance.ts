/**
 * Performance Monitoring & Optimization
 */

import { useEffect } from "react";

/**
 * Track page load performance
 */
export function usePerformanceMetrics() {
  useEffect(() => {
    if (typeof window === "undefined") return;

    // Wait for page load
    window.addEventListener("load", () => {
      const perfData = window.performance.getEntriesByType(
        "navigation"
      )[0] as PerformanceNavigationTiming;

      if (perfData) {
        const metrics = {
          dns: perfData.domainLookupEnd - perfData.domainLookupStart,
          tcp: perfData.connectEnd - perfData.connectStart,
          ttfb: perfData.responseStart - perfData.requestStart,
          download: perfData.responseEnd - perfData.responseStart,
          domInteractive: perfData.domInteractive - perfData.fetchStart,
          domComplete: perfData.domComplete - perfData.fetchStart,
          loadComplete: perfData.loadEventEnd - perfData.fetchStart,
        };

        if (process.env.NODE_ENV === "development") {
          console.table(metrics);
        }

        return metrics;
      }
    });
  }, []);
}

/**
 * Measure rendering performance
 */
export function measureRender(componentName: string) {
  const start = performance.now();

  return () => {
    const end = performance.now();
    const duration = end - start;

    if (process.env.NODE_ENV === "development" && duration > 16.67) {
      console.warn(
        `${componentName} took ${duration.toFixed(2)}ms to render (exceeds 60fps)`
      );
    }
  };
}

/**
 * Debounce function for performance
 */
export function debounce<T extends (...args: any[]) => any>(
  fn: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: NodeJS.Timeout;

  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn(...args), delay);
  };
}

/**
 * Throttle function for performance
 */
export function throttle<T extends (...args: any[]) => any>(
  fn: T,
  delay: number
): (...args: Parameters<T>) => void {
  let lastCall = 0;
  let timeoutId: NodeJS.Timeout;

  return (...args: Parameters<T>) => {
    const now = Date.now();

    if (now - lastCall >= delay) {
      fn(...args);
      lastCall = now;
    } else {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(
        () => {
          fn(...args);
          lastCall = Date.now();
        },
        delay - (now - lastCall)
      );
    }
  };
}

/**
 * Image lazy loading
 */
export function useLazyLoadImage(imageRef: React.RefObject<HTMLImageElement>) {
  useEffect(() => {
    if (!imageRef.current) return;
    if (!("IntersectionObserver" in window)) {
      return;
    }

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          const img = entry.target as HTMLImageElement;
          const src = img.getAttribute("data-src");

          if (src) {
            img.src = src;
            img.removeAttribute("data-src");
            observer.unobserve(img);
          }
        }
      },
      { rootMargin: "50px" }
    );

    observer.observe(imageRef.current);

    return () => {
      if (imageRef.current) {
        observer.unobserve(imageRef.current);
      }
    };
  }, [imageRef]);
}

/**
 * Virtualization for long lists
 */
export interface VirtualizationConfig {
  itemHeight: number;
  containerHeight: number;
  items: any[];
  renderItem: (item: any, index: number) => React.ReactNode;
}

export function useVirtualization({
  itemHeight,
  containerHeight,
  items,
  renderItem,
}: VirtualizationConfig) {
  const visibleCount = Math.ceil(containerHeight / itemHeight);
  const [scrollTop, setScrollTop] = React.useState(0);

  const startIndex = Math.floor(scrollTop / itemHeight);
  const endIndex = Math.min(startIndex + visibleCount + 1, items.length);
  const visibleItems = items.slice(startIndex, endIndex);

  return {
    startIndex,
    endIndex,
    visibleItems,
    containerHeight,
    totalHeight: items.length * itemHeight,
    offsetY: startIndex * itemHeight,
    onScroll: (top: number) => setScrollTop(top),
  };
}

/**
 * Request idle callback polyfill
 */
export function scheduleIdleTask(callback: () => void) {
  if ("requestIdleCallback" in window) {
    window.requestIdleCallback(callback);
  } else {
    setTimeout(callback, 1);
  }
}

/**
 * Prefetch critical resources
 */
export function prefetchResource(
  url: string,
  type: "script" | "style" = "script"
) {
  const link = document.createElement("link");
  link.rel = "prefetch";
  link.href = url;
  if (type === "style") {
    link.as = "style";
  } else {
    link.as = "script";
  }
  document.head.appendChild(link);
}

/**
 * Cache API response
 */
export function createResponseCache<T>(
  fetcher: () => Promise<T>,
  ttl: number = 60000
) {
  let cached: T | null = null;
  let timestamp = 0;

  return async () => {
    const now = Date.now();

    if (cached && now - timestamp < ttl) {
      return cached;
    }

    cached = await fetcher();
    timestamp = now;
    return cached;
  };
}
