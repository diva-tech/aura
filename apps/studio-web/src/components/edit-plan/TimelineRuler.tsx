"use client";

interface TimelineRulerProps {
  duration: number;
  zoom: number;
}

export function TimelineRuler({ duration, zoom }: TimelineRulerProps) {
  const pixelsPerSecond = (zoom / 100) * 50;
  const totalWidth = Math.ceil((duration / 1000) * pixelsPerSecond);

  const marks: Array<{ time: number; label: string }> = [];
  const interval = duration > 60000 ? 5000 : 1000;

  for (let i = 0; i <= duration; i += interval) {
    const seconds = Math.floor(i / 1000);
    const minutes = Math.floor(seconds / 60);
    marks.push({
      time: i,
      label: `${minutes}:${(seconds % 60).toString().padStart(2, "0")}`,
    });
  }

  return (
    <div
      className="relative h-8 bg-gradient-to-r from-slate-900 to-slate-800/50 border-b border-slate-700 flex items-center"
      style={{ width: `${totalWidth}px` }}
    >
      {marks.map((mark, idx) => {
        const x = (mark.time / 1000) * pixelsPerSecond;
        return (
          <div
            key={idx}
            className="absolute flex flex-col items-center"
            style={{ left: `${x}px` }}
          >
            <div className="w-0.5 h-2 bg-slate-600" />
            <span className="text-xs text-slate-500 mt-0.5 whitespace-nowrap">
              {mark.label}
            </span>
          </div>
        );
      })}
    </div>
  );
}
