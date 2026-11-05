"use client";

import { motion } from "framer-motion";

interface SkeletonProps {
  className?: string;
  count?: number;
  circle?: boolean;
  lines?: number;
}

export function Skeleton({
  className = "h-4 w-full rounded-lg",
  count = 1,
  circle = false,
  lines = 1,
}: SkeletonProps) {
  const skeletons = Array.from({ length: count || lines });

  return (
    <div className="space-y-3">
      {skeletons.map((_, idx) => (
        <motion.div
          key={idx}
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 2, repeat: Infinity }}
          className={`${circle ? "rounded-full" : "rounded-lg"} bg-slate-800 ${className}`}
        />
      ))}
    </div>
  );
}

// Common skeleton patterns
export function SkeletonText() {
  return (
    <div className="space-y-2">
      <Skeleton className="h-4 w-full" />
      <Skeleton className="h-4 w-5/6" />
      <Skeleton className="h-4 w-4/6" />
    </div>
  );
}

export function SkeletonCard() {
  return (
    <div className="p-4 space-y-3">
      <Skeleton className="h-6 w-1/3" />
      <Skeleton className="h-4 w-full" />
      <Skeleton className="h-4 w-5/6" />
      <div className="flex gap-2 pt-2">
        <Skeleton className="h-8 w-20 rounded-lg" />
        <Skeleton className="h-8 w-20 rounded-lg" />
      </div>
    </div>
  );
}

export function SkeletonVideo() {
  return (
    <div className="space-y-3">
      <Skeleton className="h-40 w-full rounded-xl" />
      <Skeleton className="h-5 w-2/3" />
      <Skeleton className="h-4 w-1/3" />
    </div>
  );
}

export function SkeletonGrid({ count = 6 }: { count?: number }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {Array.from({ length: count }).map((_, idx) => (
        <SkeletonCard key={idx} />
      ))}
    </div>
  );
}
