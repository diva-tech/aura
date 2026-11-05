"use client";

import { motion } from "framer-motion";
import { Eye, Lock } from "lucide-react";
import { TimelineClip } from "./TimelineClip";

interface TimelineTrackProps {
  track: any;
  isSelected: boolean;
  onSelectClip: (clipId: string) => void;
  zoom: number;
}

export function TimelineTrack({
  track,
  isSelected,
  onSelectClip,
  zoom,
}: TimelineTrackProps) {
  const trackColors: Record<string, string> = {
    video: "bg-blue-900/30",
    audio: "bg-green-900/30",
    caption: "bg-purple-900/30",
    overlay: "bg-yellow-900/30",
    music: "bg-pink-900/30",
    transition: "bg-orange-900/30",
    zoom: "bg-cyan-900/30",
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      className="border-b border-slate-800 flex"
    >
      {/* Track header */}
      <div className="w-40 border-r border-slate-800 bg-slate-900/50 p-2 flex flex-col justify-center gap-2">
        <div className="flex items-center gap-2">
          <div
            className="w-3 h-3 rounded"
            style={{
              backgroundColor:
                track.track_type === "video" ? "#3b82f6" : "#10b981",
            }}
          />
          <span className="text-xs font-medium text-slate-300 truncate">
            {track.label}
          </span>
        </div>

        <div className="flex gap-1">
          <button className="p-1 rounded hover:bg-slate-800 text-slate-500 hover:text-white transition-colors">
            <Eye size={14} />
          </button>
          <button className="p-1 rounded hover:bg-slate-800 text-slate-500 hover:text-white transition-colors">
            <Lock size={14} />
          </button>
        </div>
      </div>

      {/* Track content */}
      <div
        className={`flex-1 relative min-h-16 ${trackColors[track.track_type] || "bg-slate-900/20"}`}
      >
        {track.clips?.map((clip: any) => (
          <TimelineClip
            key={clip.id}
            clip={clip}
            isSelected={isSelected}
            onSelect={onSelectClip}
            zoom={zoom}
          />
        ))}

        {/* Empty state */}
        {(!track.clips || track.clips.length === 0) && (
          <div className="absolute inset-0 flex items-center justify-center text-slate-600 text-xs">
            Empty
          </div>
        )}
      </div>
    </motion.div>
  );
}
