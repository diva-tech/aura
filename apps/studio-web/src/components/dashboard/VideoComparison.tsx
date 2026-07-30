"use client";

import { motion } from "framer-motion";

export function VideoComparison({ projectId }: { projectId: string }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="p-6 rounded-lg border border-slate-700 bg-slate-800/30"
    >
      <h2 className="text-lg font-semibold text-white mb-4">Compare Videos</h2>
      <div className="grid grid-cols-3 gap-6">
        <div className="text-center">
          <div className="w-24 h-24 mx-auto mb-3 rounded-lg bg-slate-700" />
          <p className="text-sm text-slate-300 mb-2">Video A</p>
          <p className="text-xs text-slate-500">12,450 views</p>
        </div>
        <div className="flex items-center justify-center">
          <div className="text-center">
            <p className="text-xs text-slate-500 mb-2">VS</p>
            <div className="text-green-400 font-bold">+28%</div>
            <p className="text-xs text-slate-500 mt-1">Higher CTR</p>
          </div>
        </div>
        <div className="text-center">
          <div className="w-24 h-24 mx-auto mb-3 rounded-lg bg-slate-700" />
          <p className="text-sm text-slate-300 mb-2">Video B</p>
          <p className="text-xs text-slate-500">9,720 views</p>
        </div>
      </div>
    </motion.div>
  );
}
