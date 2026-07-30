"use client";

import { motion } from "framer-motion";
import { Play } from "lucide-react";

interface VideoPlayerProps {
  projectId: string;
  currentTime: number;
}

export function VideoPlayer({ projectId, currentTime }: VideoPlayerProps) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-4"
    >
      {/* Video container */}
      <div className="aspect-video rounded-lg bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700 flex items-center justify-center group hover:border-slate-600 transition-colors cursor-pointer">
        <div className="flex flex-col items-center gap-3">
          <div className="w-16 h-16 rounded-full bg-white/20 backdrop-blur-md flex items-center justify-center group-hover:bg-white/30 transition-colors">
            <Play size={28} className="text-white fill-white ml-1" />
          </div>
          <span className="text-xs text-slate-400">Preview Mode</span>
        </div>
      </div>

      {/* Timeline info */}
      <div className="space-y-2">
        <div className="flex justify-between text-xs text-slate-400">
          <span>{formatTime(currentTime)}</span>
          <span>0:00</span>
        </div>
        <div className="w-full h-1 bg-slate-700 rounded-full overflow-hidden">
          <div className="h-full bg-blue-600" style={{ width: "0%" }} />
        </div>
      </div>

      {/* Project info */}
      <div className="space-y-3 pt-4 border-t border-slate-800">
        <div>
          <h3 className="text-xs font-semibold text-slate-300 uppercase mb-2">
            Project Details
          </h3>
          <div className="space-y-1 text-xs text-slate-400">
            <div className="flex justify-between">
              <span>Duration:</span>
              <span className="text-white">0:00</span>
            </div>
            <div className="flex justify-between">
              <span>Original Size:</span>
              <span className="text-white">~500MB</span>
            </div>
            <div className="flex justify-between">
              <span>Resolution:</span>
              <span className="text-white">1920×1080</span>
            </div>
          </div>
        </div>
      </div>

      {/* Edit info */}
      <div className="space-y-3 pt-4 border-t border-slate-800">
        <div>
          <h3 className="text-xs font-semibold text-slate-300 uppercase mb-2">
            Edit Statistics
          </h3>
          <div className="space-y-1 text-xs text-slate-400">
            <div className="flex justify-between">
              <span>Estimated Duration:</span>
              <span className="text-white">0:00</span>
            </div>
            <div className="flex justify-between">
              <span>Estimated Size:</span>
              <span className="text-white">~300MB</span>
            </div>
            <div className="flex justify-between">
              <span>Time Saved:</span>
              <span className="text-green-400">~2:45</span>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

function formatTime(ms: number): string {
  const seconds = Math.floor(ms / 1000);
  const minutes = Math.floor(seconds / 60);
  return `${minutes}:${(seconds % 60).toString().padStart(2, "0")}`;
}
