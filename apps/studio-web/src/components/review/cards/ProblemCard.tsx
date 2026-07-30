"use client";

import { motion } from "framer-motion";

interface ProblemCardProps {
  problem: string;
}

export default function ProblemCard({ problem }: ProblemCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      className="flex items-center gap-3 p-3 rounded-lg bg-slate-800/50 hover:bg-slate-800 transition-colors border border-slate-700"
    >
      <div className="text-yellow-400 font-bold text-lg">⚠</div>
      <span className="text-slate-200">{problem}</span>
    </motion.div>
  );
}
