"use client";

import { useRef, useState } from "react";
import { motion } from "framer-motion";
import { ChevronDown } from "lucide-react";
import { TimelineRuler } from "./TimelineRuler";
import { TimelineTrack } from "./TimelineTrack";
import { Playhead } from "./Playhead";

interface InteractiveTimelineProps {
  editPlan: any;
  selectedClipId: string | null;
  onSelectClip: (clipId: string | null) => void;
  currentTime: number;
  onTimeChange: (time: number) => void;
  zoom: number;
}

export function InteractiveTimeline({
  editPlan,
  selectedClipId,
  onSelectClip,
  currentTime,
  onTimeChange,
  zoom,
}: InteractiveTimelineProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [scrollLeft, setScrollLeft] = useState(0);

  const handleTimelineClick = (e: React.MouseEvent) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left + scrollLeft;
    const pixelsPerMs = (zoom / 100) * 0.1;
    const timeMs = x / pixelsPerMs;
    onTimeChange(Math.max(0, timeMs));
  };

  const handleScroll = (e: React.UIEvent<HTMLDivElement>) => {
    setScrollLeft(e.currentTarget.scrollLeft);
  };

  return (
    <div className="flex flex-col h-full gap-3">
      {/* Timeline ruler + playhead */}
      <div
        ref={containerRef}
        onClick={handleTimelineClick}
        onScroll={handleScroll}
        className="flex-1 overflow-auto bg-slate-900/50 rounded-lg border border-slate-800 relative"
      >
        <div className="relative">
          <TimelineRuler
            duration={editPlan?.estimated_duration || 0}
            zoom={zoom}
          />

          <Playhead
            currentTime={currentTime}
            duration={editPlan?.estimated_duration || 0}
            zoom={zoom}
          />

          {/* Tracks */}
          <div className="relative">
            {editPlan?.tracks?.map((track: any, idx: number) => (
              <TimelineTrack
                key={track.id}
                track={track}
                isSelected={selectedClipId !== null}
                onSelectClip={onSelectClip}
                zoom={zoom}
              />
            ))}
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="flex items-center gap-2">
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => setIsPlaying(!isPlaying)}
          className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium transition-colors"
        >
          {isPlaying ? "Pause" : "Play"}
        </motion.button>

        <div className="text-xs text-slate-400 font-mono">
          {formatTime(currentTime)} /{" "}
          {formatTime(editPlan?.estimated_duration || 0)}
        </div>

        <div className="flex-1" />

        <div className="text-xs text-slate-500">
          {editPlan?.operations?.length || 0} operations •{" "}
          {editPlan?.change_count || 0} changes
        </div>
      </div>
    </div>
  );
}

function formatTime(ms: number): string {
  const seconds = Math.floor(ms / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);

  if (hours > 0) {
    return `${hours}:${(minutes % 60).toString().padStart(2, "0")}:${(
      seconds % 60
    )
      .toString()
      .padStart(2, "0")}`;
  }

  return `${minutes}:${(seconds % 60).toString().padStart(2, "0")}`;
}
