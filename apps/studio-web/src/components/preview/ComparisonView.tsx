"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Play, Maximize2, Volume2 } from "lucide-react";

interface ComparisonViewProps {
  projectId: string;
  currentTime: number;
  onTimeChange: (time: number) => void;
}

export function ComparisonView({
  projectId,
  currentTime,
  onTimeChange,
}: ComparisonViewProps) {
  const [viewMode, setViewMode] = useState<"split" | "toggle" | "overlay">(
    "split"
  );
  const [isPlaying, setIsPlaying] = useState(false);

  return (
    <div className="h-full flex flex-col">
      {/* View mode selector */}
      <div className="h-12 border-b border-slate-800 bg-slate-900/50 px-4 flex items-center justify-between">
        <div className="flex gap-2">
          <button
            onClick={() => setViewMode("split")}
            className={`px-3 py-1.5 rounded text-xs font-medium transition-colors ${
              viewMode === "split"
                ? "bg-blue-600 text-white"
                : "bg-slate-800 text-slate-300 hover:bg-slate-700"
            }`}
          >
            Split View
          </button>
          <button
            onClick={() => setViewMode("toggle")}
            className={`px-3 py-1.5 rounded text-xs font-medium transition-colors ${
              viewMode === "toggle"
                ? "bg-blue-600 text-white"
                : "bg-slate-800 text-slate-300 hover:bg-slate-700"
            }`}
          >
            Toggle
          </button>
          <button
            onClick={() => setViewMode("overlay")}
            className={`px-3 py-1.5 rounded text-xs font-medium transition-colors ${
              viewMode === "overlay"
                ? "bg-blue-600 text-white"
                : "bg-slate-800 text-slate-300 hover:bg-slate-700"
            }`}
          >
            Overlay
          </button>
        </div>

        <div className="text-xs text-slate-400">
          {formatTime(currentTime)} / 0:00
        </div>
      </div>

      {/* Video players */}
      <div className="flex-1 overflow-hidden p-4">
        {viewMode === "split" && (
          <div className="h-full grid grid-cols-2 gap-4">
            {/* Original */}
            <VideoPlayer label="Original" />
            {/* Preview */}
            <VideoPlayer label="Preview" isPreview />
          </div>
        )}

        {viewMode === "toggle" && (
          <div className="h-full relative">
            <VideoPlayer label="Original" isFullScreen />
            <motion.div
              className="absolute bottom-4 right-4 px-3 py-1.5 rounded-lg bg-blue-600/80 text-white text-xs font-medium backdrop-blur-sm"
              animate={{ opacity: [0.7, 1, 0.7] }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              Click to toggle
            </motion.div>
          </div>
        )}

        {viewMode === "overlay" && (
          <div className="h-full relative">
            <VideoPlayer label="Original" isFullScreen />
            <motion.div
              className="absolute top-4 right-4 w-32 h-20 rounded-lg border-2 border-blue-500 bg-black/50 overflow-hidden"
              whileHover={{ scale: 1.1 }}
            >
              <div className="w-full h-full bg-gradient-to-br from-blue-600/30 to-transparent flex items-center justify-center">
                <Play size={16} className="text-blue-300" />
              </div>
              <div className="absolute bottom-2 left-2 text-xs text-blue-300 font-medium">
                Preview
              </div>
            </motion.div>
          </div>
        )}
      </div>

      {/* Timeline */}
      <div className="h-24 border-t border-slate-800 bg-slate-900/50 p-4 space-y-2">
        <div className="flex items-center gap-2">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setIsPlaying(!isPlaying)}
            className="px-4 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium transition-colors flex items-center gap-2"
          >
            <Play size={16} />
            {isPlaying ? "Pause" : "Play"}
          </motion.button>

          <div className="flex-1 h-12 bg-slate-800 rounded-lg border border-slate-700 overflow-hidden">
            <div className="h-full bg-gradient-to-r from-blue-600/20 to-transparent" />
          </div>
        </div>

        <div className="flex items-center justify-between text-xs text-slate-400">
          <span>Timeline with operation markers</span>
          <span>0 changes • 8 operations</span>
        </div>
      </div>
    </div>
  );
}

function VideoPlayer({
  label,
  isPreview,
  isFullScreen,
}: {
  label: string;
  isPreview?: boolean;
  isFullScreen?: boolean;
}) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className={`rounded-xl bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700 flex items-center justify-center group hover:border-slate-600 transition-colors cursor-pointer ${
        isFullScreen ? "h-full" : "h-full"
      }`}
    >
      <div className="flex flex-col items-center gap-3">
        <div className="w-20 h-20 rounded-full bg-white/20 backdrop-blur-md flex items-center justify-center group-hover:bg-white/30 transition-colors">
          <Play size={32} className="text-white fill-white ml-1" />
        </div>
        <span
          className={`text-sm font-medium ${isPreview ? "text-blue-400" : "text-slate-300"}`}
        >
          {label}
        </span>
      </div>
    </motion.div>
  );
}

function formatTime(ms: number): string {
  const seconds = Math.floor(ms / 1000);
  const minutes = Math.floor(seconds / 60);
  return `${minutes}:${(seconds % 60).toString().padStart(2, "0")}`;
}
