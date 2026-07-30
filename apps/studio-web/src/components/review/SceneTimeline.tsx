"use client";

import { motion } from "framer-motion";

interface SceneTimelineProps {
  scenes: any[];
}

export default function SceneTimeline({ scenes }: SceneTimelineProps) {
  return (
    <div className="px-6 py-4 border-t border-slate-800">
      <h3 className="text-sm font-semibold text-slate-300 mb-3">Timeline</h3>
      <div className="flex gap-2 overflow-x-auto pb-2">
        {scenes?.map((scene, idx) => (
          <motion.button
            key={idx}
            whileHover={{ scale: 1.05 }}
            className="flex-shrink-0 h-20 w-24 rounded-lg bg-gradient-to-b from-slate-700 to-slate-800 border border-slate-600 hover:border-slate-500 transition-colors flex flex-col items-center justify-center text-center gap-1 p-2 group"
          >
            <div className="text-xs font-medium text-slate-300 group-hover:text-white">
              Scene {idx + 1}
            </div>
            <div className="text-xs text-slate-400">{scene.emotion}</div>
          </motion.button>
        ))}
      </div>
    </div>
  );
}
