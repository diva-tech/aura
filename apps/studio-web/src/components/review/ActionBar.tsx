"use client";

import { motion } from "framer-motion";
import { Check, X, FileText } from "lucide-react";

interface ActionBarProps {
  acceptedCount: number;
  totalSuggestions: number;
}

export default function ActionBar({
  acceptedCount,
  totalSuggestions,
}: ActionBarProps) {
  const isReadyForPlan = acceptedCount > 0;

  return (
    <motion.div
      initial={{ y: 100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      className="fixed bottom-0 left-0 right-0 border-t border-slate-800 bg-gradient-to-t from-slate-950 via-slate-900 to-slate-900/80 backdrop-blur-xl px-8 py-4"
    >
      <div className="flex items-center justify-between max-w-full">
        <div className="text-sm text-slate-400">
          <span className="text-white font-medium">{acceptedCount}</span> of{" "}
          <span className="text-white font-medium">{totalSuggestions}</span>{" "}
          suggestions accepted
        </div>

        <div className="flex items-center gap-3">
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-white text-sm font-medium transition-colors flex items-center gap-2"
          >
            <X size={16} />
            Reject All
          </motion.button>

          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-white text-sm font-medium transition-colors flex items-center gap-2"
          >
            <Check size={16} />
            Accept All
          </motion.button>

          <motion.button
            whileHover={{ scale: isReadyForPlan ? 1.02 : 1 }}
            whileTap={{ scale: 0.98 }}
            disabled={!isReadyForPlan}
            className="px-6 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <FileText size={16} />
            Generate Edit Plan
          </motion.button>
        </div>
      </div>
    </motion.div>
  );
}
