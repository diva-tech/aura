"use client";

import { motion } from "framer-motion";
import { TrendingUp } from "lucide-react";

export function ForecastPanel({ projectId }: { projectId: string }) {
  const forecasts = [
    { label: "Predicted Views", value: "15,200", confidence: "92%" },
    { label: "Expected CTR", value: "8.5%", confidence: "87%" },
    { label: "Watch Time Trend", value: "+22%", confidence: "89%" },
    { label: "Revenue Forecast", value: "$1,650", confidence: "85%" },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="p-6 rounded-lg border border-slate-700 bg-slate-800/30"
    >
      <div className="flex items-center gap-2 mb-4">
        <TrendingUp size={20} className="text-blue-400" />
        <h2 className="text-lg font-semibold text-white">
          Next Week Forecast (M14)
        </h2>
      </div>
      <div className="grid grid-cols-4 gap-3">
        {forecasts.map((forecast, idx) => (
          <motion.div
            key={idx}
            whileHover={{ scale: 1.05 }}
            className="p-4 rounded-lg bg-slate-900/50 border border-slate-700/50"
          >
            <p className="text-xs text-slate-400 mb-2">{forecast.label}</p>
            <p className="text-xl font-bold text-white mb-2">
              {forecast.value}
            </p>
            <p className="text-xs text-blue-400">
              Confidence: {forecast.confidence}
            </p>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
