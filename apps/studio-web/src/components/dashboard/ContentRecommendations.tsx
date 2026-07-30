"use client";

import { motion } from "framer-motion";
import { Lightbulb } from "lucide-react";

const recommendations = [
  { title: "Trending: AI in 2026", impact: "+45%", priority: "High" },
  { title: "Add YouTube Shorts Version", impact: "+28%", priority: "High" },
  { title: "Longer Intro Hook", impact: "+18%", priority: "Medium" },
  { title: "Use Pattern Interrupts", impact: "+15%", priority: "Medium" },
];

export function ContentRecommendations({ projectId }: { projectId: string }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="p-6 rounded-lg border border-slate-700 bg-slate-800/30"
    >
      <div className="flex items-center gap-2 mb-4">
        <Lightbulb size={20} className="text-yellow-400" />
        <h2 className="text-lg font-semibold text-white">Recommendations</h2>
      </div>
      <div className="space-y-2">
        {recommendations.map((rec, idx) => (
          <motion.div
            key={idx}
            whileHover={{ x: 4 }}
            className="p-3 rounded-lg bg-slate-900/50 border border-slate-700/50"
          >
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-300">{rec.title}</span>
              <div className="flex items-center gap-2">
                <span className="text-xs font-semibold text-green-400">
                  {rec.impact}
                </span>
                <span className="text-xs px-1.5 py-0.5 rounded bg-slate-700 text-slate-300">
                  {rec.priority}
                </span>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
