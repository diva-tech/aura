"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Trash2, Copy } from "lucide-react";

interface TimelineClipProps {
  clip: any;
  isSelected: boolean;
  onSelect: (clipId: string) => void;
  zoom: number;
}

export function TimelineClip({
  clip,
  isSelected,
  onSelect,
  zoom,
}: TimelineClipProps) {
  const [isHovering, setIsHovering] = useState(false);
  const pixelsPerMs = (zoom / 100) * 0.1;

  const left = clip.start_time * pixelsPerMs;
  const width = Math.max(4, (clip.end_time - clip.start_time) * pixelsPerMs);

  const clipColors: Record<string, string> = {
    video: "from-blue-600 to-blue-700",
    audio: "from-green-600 to-green-700",
    text: "from-purple-600 to-purple-700",
    effect: "from-yellow-600 to-yellow-700",
    music: "from-pink-600 to-pink-700",
  };

  return (
    <motion.div
      layout
      onMouseEnter={() => setIsHovering(true)}
      onMouseLeave={() => setIsHovering(false)}
      onClick={(e) => {
        e.stopPropagation();
        onSelect(clip.id);
      }}
      className={`absolute top-1 bottom-1 rounded-md border-2 cursor-pointer transition-all ${
        isSelected
          ? "border-blue-400 ring-2 ring-blue-500/50"
          : "border-slate-600 hover:border-slate-500"
      } bg-gradient-to-r ${clipColors[clip.clip_type] || "from-slate-600 to-slate-700"} group`}
      style={{
        left: `${left}px`,
        width: `${width}px`,
      }}
    >
      {/* Clip label */}
      <div className="px-2 py-1 text-xs font-medium text-white truncate">
        {clip.title || clip.clip_type}
      </div>

      {/* Resize handles */}
      {isSelected && (
        <>
          <div className="absolute left-0 top-0 bottom-0 w-1 bg-blue-400 cursor-col-resize hover:w-2 transition-all" />
          <div className="absolute right-0 top-0 bottom-0 w-1 bg-blue-400 cursor-col-resize hover:w-2 transition-all" />
        </>
      )}

      {/* Hover actions */}
      {isHovering && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="absolute -top-8 right-0 flex gap-1 bg-slate-800 p-1 rounded border border-slate-700"
        >
          <button
            onClick={(e) => {
              e.stopPropagation();
            }}
            className="p-1 rounded hover:bg-slate-700 text-slate-400 hover:text-white transition-colors"
            title="Duplicate"
          >
            <Copy size={14} />
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
            }}
            className="p-1 rounded hover:bg-slate-700 text-slate-400 hover:text-red-400 transition-colors"
            title="Delete"
          >
            <Trash2 size={14} />
          </button>
        </motion.div>
      )}
    </motion.div>
  );
}
