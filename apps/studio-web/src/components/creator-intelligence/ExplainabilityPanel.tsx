"use client";

import { motion } from "framer-motion";
import {
  ChevronRight,
  CheckCircle,
  AlertCircle,
  TrendingUp,
  Zap,
} from "lucide-react";

interface ExplanationProps {
  operation: string;
  reason: string;
  confidence: number;
  expectedImprovement: {
    metric: string;
    improvement: string;
  }[];
  dataSources: string[];
  alternatives: string[];
}

export function ExplainabilityPanel({
  operation,
  reason,
  confidence,
  expectedImprovement,
  dataSources,
  alternatives,
}: ExplanationProps) {
  const confidenceColor =
    confidence >= 0.9
      ? "text-green-400"
      : confidence >= 0.8
        ? "text-blue-400"
        : "text-yellow-400";

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6 p-6 rounded-lg border border-slate-700 bg-slate-800/30"
    >
      {/* Operation Header */}
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <CheckCircle size={20} className="text-green-400" />
          <h2 className="text-xl font-bold text-white">{operation}</h2>
        </div>
        <p className="text-slate-400 text-sm">
          AI Recommendation with detailed reasoning
        </p>
      </div>

      {/* Reason */}
      <div className="space-y-2">
        <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wide">
          Reason
        </h3>
        <p className="text-white leading-relaxed">{reason}</p>
      </div>

      {/* Confidence */}
      <div className="space-y-2">
        <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wide">
          Confidence
        </h3>
        <div className="flex items-center gap-4">
          <div className="flex-1 h-2 bg-slate-700 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${confidence * 100}%` }}
              transition={{ duration: 0.8 }}
              className={`h-full ${
                confidence >= 0.9
                  ? "bg-green-500"
                  : confidence >= 0.8
                    ? "bg-blue-500"
                    : "bg-yellow-500"
              }`}
            />
          </div>
          <span className={`font-bold text-lg ${confidenceColor}`}>
            {(confidence * 100).toFixed(0)}%
          </span>
        </div>
      </div>

      {/* Expected Improvements */}
      <div className="space-y-3">
        <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wide">
          Expected Improvements
        </h3>
        <div className="space-y-2">
          {expectedImprovement.map((item, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.1 }}
              className="flex items-center justify-between p-3 rounded-lg bg-slate-900/50"
            >
              <div className="flex items-center gap-2">
                <TrendingUp size={16} className="text-green-400" />
                <span className="text-sm text-slate-300">{item.metric}</span>
              </div>
              <span className="font-semibold text-green-400">
                {item.improvement}
              </span>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Data Sources */}
      <div className="space-y-3">
        <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wide">
          Data Sources
        </h3>
        <div className="flex flex-wrap gap-2">
          {dataSources.map((source, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: idx * 0.05 }}
              className="px-3 py-1 rounded-full bg-blue-500/20 border border-blue-500/50"
            >
              <p className="text-xs font-medium text-blue-300">{source}</p>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Alternative Suggestions */}
      <div className="space-y-3">
        <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wide">
          Alternative Options
        </h3>
        <div className="space-y-2">
          {alternatives.map((alt, idx) => (
            <motion.div
              key={idx}
              whileHover={{ x: 4 }}
              className="flex items-center gap-3 p-3 rounded-lg border border-slate-700 bg-slate-900/30 hover:bg-slate-900/50 transition-colors cursor-pointer"
            >
              <AlertCircle size={16} className="text-slate-500" />
              <span className="text-sm text-slate-300 flex-1">{alt}</span>
              <ChevronRight size={16} className="text-slate-500" />
            </motion.div>
          ))}
        </div>
      </div>
    </motion.div>
  );
}
