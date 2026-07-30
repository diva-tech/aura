"use client";

import { motion } from "framer-motion";

interface StrengthCardProps {
  strength: string;
}

export default function StrengthCard({ strength }: StrengthCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      className="flex items-center gap-3 p-3 rounded-lg bg-slate-800/50 hover:bg-slate-800 transition-colors border border-slate-700"
    >
      <div className="text-green-400 font-bold text-lg">✓</div>
      <span className="text-slate-200">{strength}</span>
    </motion.div>
  );
}
