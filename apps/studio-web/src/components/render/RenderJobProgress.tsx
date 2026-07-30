"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown, Pause, Play, X } from "lucide-react";

interface RenderJobProgressProps {
  render: any;
  isCurrent?: boolean;
}

const stages = [
  { name: "Preparing Assets", icon: "📦" },
  { name: "Cutting", icon: "✂️" },
  { name: "Captions", icon: "📝" },
  { name: "Overlays", icon: "🎨" },
  { name: "Transitions", icon: "🔄" },
  { name: "Effects", icon: "✨" },
  { name: "Audio Mix", icon: "🔊" },
  { name: "Color Grading", icon: "🎬" },
  { name: "Encoding", icon: "⚙️" },
  { name: "Thumbnail", icon: "🖼️" },
];

export function RenderJobProgress({
  render,
  isCurrent,
}: RenderJobProgressProps) {
  const [isExpanded, setIsExpanded] = useState(isCurrent);

  const completedStages = Math.floor((render.progress_percent || 0) / 10);

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`rounded-lg border transition-all ${
        isCurrent
          ? "border-blue-500 bg-blue-500/10"
          : "border-slate-700 bg-slate-800/30"
      }`}
    >
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-4 py-3 text-left flex items-center justify-between hover:bg-slate-800/20 transition-colors"
      >
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <span className="font-semibold text-white">
              Render v{render.version || 1}
            </span>
            <span
              className={`text-xs px-2 py-1 rounded-full ${
                isCurrent
                  ? "bg-blue-900/50 text-blue-300"
                  : "bg-slate-700/50 text-slate-300"
              }`}
            >
              {render.status}
            </span>
          </div>
          <div className="w-full h-2 bg-slate-700 rounded-full overflow-hidden">
            <motion.div
              className={`h-full ${isCurrent ? "bg-blue-500" : "bg-slate-600"}`}
              initial={{ width: "0%" }}
              animate={{ width: `${render.progress_percent || 0}%` }}
              transition={{ duration: 0.3 }}
            />
          </div>
          <div className="flex items-center justify-between mt-2 text-xs text-slate-400">
            <span>{render.current_stage || "Preparing"}</span>
            <span className="font-mono text-white">
              {Math.round(render.progress_percent || 0)}%
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2 ml-4">
          {isCurrent && (
            <>
              <button className="p-1.5 rounded hover:bg-slate-700 text-slate-400 hover:text-white transition-colors">
                <Pause size={16} />
              </button>
              <button className="p-1.5 rounded hover:bg-slate-700 text-slate-400 hover:text-white transition-colors">
                <X size={16} />
              </button>
            </>
          )}
          <ChevronDown
            size={18}
            className={`text-slate-500 transition-transform ${
              isExpanded ? "rotate-180" : ""
            }`}
          />
        </div>
      </button>

      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="border-t border-slate-700/50 px-4 py-3 space-y-2"
          >
            <div className="grid grid-cols-5 gap-2">
              {stages.map((stage, idx) => (
                <div
                  key={stage.name}
                  className={`p-2 rounded text-center text-xs transition-colors ${
                    idx < completedStages
                      ? "bg-green-900/30 text-green-300"
                      : idx === completedStages
                        ? "bg-blue-900/30 text-blue-300 animate-pulse"
                        : "bg-slate-700/30 text-slate-500"
                  }`}
                >
                  <div className="text-base mb-1">{stage.icon}</div>
                  <div className="truncate">{stage.name}</div>
                </div>
              ))}
            </div>

            <div className="grid grid-cols-3 gap-2 pt-2 border-t border-slate-700/30 text-xs">
              <div>
                <p className="text-slate-500">Elapsed</p>
                <p className="text-white font-medium">
                  {Math.floor((render.elapsed_time || 0) / 60)}m
                </p>
              </div>
              <div>
                <p className="text-slate-500">ETA</p>
                <p className="text-white font-medium">
                  {Math.floor((render.estimated_time || 120) / 60)}m
                </p>
              </div>
              <div>
                <p className="text-slate-500">Output</p>
                <p className="text-white font-medium">
                  {Math.round((render.output_size || 0) / 1024 / 1024)}MB
                </p>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
