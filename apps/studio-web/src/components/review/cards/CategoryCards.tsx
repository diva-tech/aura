"use client";

import { motion } from "framer-motion";

interface CategoryCardsProps {
  scores: any;
}

export default function CategoryCards({ scores }: CategoryCardsProps) {
  const categories = [
    { label: "Content", score: scores?.overall_score || 75 },
    { label: "Hook", score: scores?.hook_score || 65 },
    { label: "Audio", score: scores?.audio_score || 82 },
    { label: "Visual", score: scores?.visual_score || 80 },
    { label: "Editing", score: 72 },
    { label: "SEO", score: 68 },
  ];

  return (
    <div>
      <h3 className="text-lg font-semibold text-white mb-4">
        Review Categories
      </h3>
      <div className="grid grid-cols-2 gap-4">
        {categories.map((cat, idx) => {
          const color =
            cat.score >= 80
              ? "from-green-600 to-green-700"
              : cat.score >= 70
                ? "from-blue-600 to-blue-700"
                : "from-yellow-600 to-yellow-700";

          return (
            <motion.div
              key={idx}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: idx * 0.05 }}
              className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-xl p-4 border border-slate-700 hover:border-slate-600 transition-colors"
            >
              <div className="flex items-center justify-between mb-3">
                <span className="text-sm font-medium text-slate-300">
                  {cat.label}
                </span>
                <span className="text-lg font-bold text-white">
                  {cat.score}
                </span>
              </div>
              <div className="w-full bg-slate-700 rounded-full h-2 overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${cat.score}%` }}
                  transition={{ delay: 0.3, duration: 1 }}
                  className={`h-full bg-gradient-to-r ${color} rounded-full`}
                />
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
