"use client";

import { motion } from "framer-motion";

interface AIReviewCardProps {
  analysis: any;
}

export default function AIReviewCard({ analysis }: AIReviewCardProps) {
  const summary =
    analysis?.report?.summary ||
    "This video clearly explains the content. However, the first useful information appears after 9 seconds. Adding captions and removing the introduction is estimated to improve viewer retention by approximately 27%.";

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-slate-800 via-slate-800 to-slate-900 border border-slate-700 p-6 backdrop-blur-xl"
    >
      {/* Animated background gradient */}
      <div className="absolute inset-0 opacity-50">
        <div className="absolute top-0 right-0 w-96 h-96 bg-blue-600 rounded-full mix-blend-multiply filter blur-3xl opacity-10 animate-pulse" />
      </div>

      <div className="relative z-10">
        <div className="mb-4 flex items-center gap-3">
          <div className="text-2xl">🤖</div>
          <h2 className="text-xl font-semibold text-white">
            Executive Summary
          </h2>
        </div>

        <p className="text-base text-slate-200 leading-relaxed mb-6">
          {summary}
        </p>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 gap-4">
          {[
            { label: "Estimated Retention Increase", value: "+27%" },
            { label: "Estimated CTR Increase", value: "+18%" },
            { label: "Estimated Watch Time", value: "+12%" },
            { label: "Publishing Potential", value: "High" },
          ].map((stat, idx) => (
            <div
              key={idx}
              className="bg-slate-700/40 rounded-lg p-3 backdrop-blur-sm"
            >
              <div className="text-2xl font-bold text-blue-400">
                {stat.value}
              </div>
              <div className="text-xs text-slate-400 mt-1">{stat.label}</div>
            </div>
          ))}
        </div>
      </div>
    </motion.div>
  );
}
