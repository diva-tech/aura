"use client";

import { motion } from "framer-motion";
import { Brain, CheckCircle } from "lucide-react";

const insights = [
  { title: "Audience Prefers", value: "9 PM Upload Time", impact: "High" },
  { title: "Optimal Length", value: "8-12 minutes", impact: "High" },
  {
    title: "Thumbnail Style",
    value: "Bright colors with text",
    impact: "Medium",
  },
  { title: "Hook Duration", value: "First 3 seconds critical", impact: "High" },
];

export function LearningInsights({ projectId }: { projectId: string }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="p-6 rounded-lg border border-slate-700 bg-slate-800/30"
    >
      <div className="flex items-center gap-2 mb-4">
        <Brain size={20} className="text-purple-400" />
        <h2 className="text-lg font-semibold text-white">AI Learned</h2>
      </div>
      <div className="space-y-3">
        {insights.map((insight, idx) => (
          <motion.div
            key={idx}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.1 }}
            className="flex items-start gap-3 p-3 rounded-lg bg-slate-900/50"
          >
            <CheckCircle
              size={16}
              className="text-green-400 mt-1 flex-shrink-0"
            />
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-slate-300">
                {insight.title}
              </p>
              <p className="text-xs text-white font-semibold mt-1">
                {insight.value}
              </p>
            </div>
            <span className="text-xs px-2 py-1 rounded-full bg-green-900/30 text-green-300 whitespace-nowrap">
              {insight.impact}
            </span>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
