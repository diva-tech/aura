"use client";

interface PlayheadProps {
  currentTime: number;
  duration: number;
  zoom: number;
}

export function Playhead({ currentTime, duration, zoom }: PlayheadProps) {
  const pixelsPerSecond = (zoom / 100) * 50;
  const position = (currentTime / 1000) * pixelsPerSecond;

  return (
    <div
      className="absolute top-0 bottom-0 w-0.5 bg-red-500 pointer-events-none z-10"
      style={{ left: `${position}px` }}
    >
      <div className="absolute -top-1 -left-1.5 w-4 h-4 bg-red-500 rounded-full border-2 border-red-400" />
    </div>
  );
}
