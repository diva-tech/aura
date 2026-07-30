"use client";

import { motion } from "framer-motion";
import {
  Sparkles,
  TrendingUp,
  Target,
  AlertCircle,
  CheckCircle,
} from "lucide-react";

interface Insight {
  id: string;
  type: "performance" | "opportunity" | "trend" | "alert";
  title: string;
  description: string;
  confidence: number;
  source: string;
  actionable: boolean;
}

interface InsightsFeedProps {
  insights: Insight[];
  onSelect?: (insight: Insight) => void;
}

const typeConfig = {
  performance: {
    icon: TrendingUp,
    color: "text-blue-400",
    bgColor: "bg-blue-500/10",
    borderColor: "border-blue-500/50",
  },
  opportunity: {
    icon: Target,
    color: "text-green-400",
    bgColor: "bg-green-500/10",
    borderColor: "border-green-500/50",
  },
  trend: {
    icon: Sparkles,
    color: "text-purple-400",
    bgColor: "bg-purple-500/10",
    borderColor: "border-purple-500/50",
  },
  alert: {
    icon: AlertCircle,
    color: "text-amber-400",
    bgColor: "bg-amber-500/10",
    borderColor: "border-amber-500/50",
  },
};

export function InsightsFeed({ insights, onSelect }: InsightsFeedProps) {
  return (
    <div className="space-y-3">
      {insights.length === 0 ? (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="p-6 text-center rounded-lg border border-slate-700 bg-slate-800/20"
        >
          <Sparkles size={24} className="mx-auto mb-2 text-slate-500" />
          <p className="text-slate-400">No insights yet. Keep creating!</p>
        </motion.div>
      ) : (
        insights.map((insight, idx) => {
          const config = typeConfig[insight.type];
          const Icon = config.icon;

          return (
            <motion.div
              key={insight.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.05 }}
              onClick={() => onSelect?.(insight)}
              className={`p-4 rounded-lg border ${config.borderColor} ${config.bgColor} cursor-pointer hover:bg-slate-800/30 transition-all group`}
            >
              <div className="flex gap-3">
                <Icon
                  size={20}
                  className={`${config.color} mt-1 flex-shrink-0`}
                />
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-white mb-1 truncate">
                    {insight.title}
                  </h3>
                  <p className="text-sm text-slate-300 mb-2 line-clamp-2">
                    {insight.description}
                  </p>
                  <div className="flex items-center justify-between gap-2">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-xs text-slate-500">
                        {insight.source}
                      </span>
                      <div className="flex items-center gap-1">
                        <div className="w-8 h-1 bg-slate-700 rounded-full overflow-hidden">
                          <motion.div
                            initial={{ width: 0 }}
                            animate={{
                              width: `${insight.confidence * 100}%`,
                            }}
                            transition={{ duration: 0.6 }}
                            className="h-full bg-blue-500"
                          />
                        </div>
                        <span className="text-xs text-slate-400">
                          {(insight.confidence * 100).toFixed(0)}%
                        </span>
                      </div>
                    </div>
                    {insight.actionable && (
                      <CheckCircle
                        size={16}
                        className="text-green-400 flex-shrink-0"
                      />
                    )}
                  </div>
                </div>
              </div>
            </motion.div>
          );
        })
      )}
    </div>
  );
}
