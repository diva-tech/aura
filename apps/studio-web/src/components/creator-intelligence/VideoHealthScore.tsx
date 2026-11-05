"use client";

import { motion } from "framer-motion";
import { AlertCircle, CheckCircle, TrendingUp } from "lucide-react";

interface HealthScoreProps {
  overallScore: number;
  hookScore: number;
  retentionScore: number;
  editingScore: number;
  captionsScore: number;
  thumbnailScore: number;
  seoScore: number;
  ctaScore: number;
  storytellingScore: number;
  pacingScore: number;
  brandConsistencyScore: number;
  recommendations: string[];
}

const dimensions = [
  { label: "Hook", key: "hookScore" },
  { label: "Retention", key: "retentionScore" },
  { label: "Editing", key: "editingScore" },
  { label: "Captions", key: "captionsScore" },
  { label: "Thumbnail", key: "thumbnailScore" },
  { label: "SEO", key: "seoScore" },
  { label: "CTA", key: "ctaScore" },
  { label: "Storytelling", key: "storytellingScore" },
  { label: "Pacing", key: "pacingScore" },
  { label: "Brand", key: "brandConsistencyScore" },
];

export function VideoHealthScore({
  overallScore,
  hookScore,
  retentionScore,
  editingScore,
  captionsScore,
  thumbnailScore,
  seoScore,
  ctaScore,
  storytellingScore,
  pacingScore,
  brandConsistencyScore,
  recommendations,
}: HealthScoreProps) {
  const scores = {
    hookScore,
    retentionScore,
    editingScore,
    captionsScore,
    thumbnailScore,
    seoScore,
    ctaScore,
    storytellingScore,
    pacingScore,
    brandConsistencyScore,
  };

  const getScoreColor = (score: number) => {
    if (score >= 85) return "text-green-400";
    if (score >= 75) return "text-blue-400";
    if (score >= 65) return "text-yellow-400";
    return "text-red-400";
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 85) return "bg-green-500/20";
    if (score >= 75) return "bg-blue-500/20";
    if (score >= 65) return "bg-yellow-500/20";
    return "bg-red-500/20";
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6 p-6 rounded-lg border border-slate-700 bg-slate-800/30"
    >
      {/* Overall Score */}
      <div className="text-center">
        <h2 className="text-lg font-semibold text-white mb-4">Video Health</h2>
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: "spring", stiffness: 100 }}
          className="w-32 h-32 mx-auto mb-4 rounded-full bg-gradient-to-br from-blue-500/20 to-purple-500/20 border-2 border-blue-500/50 flex items-center justify-center"
        >
          <div className="text-center">
            <div className="text-4xl font-bold text-white">
              {overallScore.toFixed(0)}
            </div>
            <div className="text-xs text-slate-400 mt-1">out of 100</div>
          </div>
        </motion.div>
      </div>

      {/* Individual Scores Grid */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        {dimensions.map((dim, idx) => {
          const score = scores[dim.key as keyof typeof scores];
          return (
            <motion.div
              key={dim.key}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: idx * 0.05 }}
              className={`p-3 rounded-lg border border-slate-700 ${getScoreBgColor(score)}`}
            >
              <p className="text-xs text-slate-400 mb-1 font-medium">
                {dim.label}
              </p>
              <p className={`text-lg font-bold ${getScoreColor(score)}`}>
                {score.toFixed(0)}
              </p>
              <div className="h-1 bg-slate-700 rounded-full mt-2 overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${score}%` }}
                  transition={{ duration: 0.8, delay: idx * 0.05 }}
                  className={`h-full ${
                    score >= 85
                      ? "bg-green-500"
                      : score >= 75
                        ? "bg-blue-500"
                        : score >= 65
                          ? "bg-yellow-500"
                          : "bg-red-500"
                  }`}
                />
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Recommendations */}
      <div className="space-y-3">
        <div className="flex items-center gap-2">
          <AlertCircle size={18} className="text-amber-400" />
          <h3 className="font-semibold text-white">Recommendations</h3>
        </div>
        <div className="space-y-2">
          {recommendations.length > 0 ? (
            recommendations.map((rec, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.1 }}
                className="flex items-start gap-2 p-3 rounded-lg bg-amber-500/10 border border-amber-500/50"
              >
                <AlertCircle
                  size={16}
                  className="text-amber-400 mt-0.5 flex-shrink-0"
                />
                <p className="text-sm text-amber-200">{rec}</p>
              </motion.div>
            ))
          ) : (
            <div className="flex items-center gap-2 p-3 rounded-lg bg-green-500/10 border border-green-500/50">
              <CheckCircle size={16} className="text-green-400" />
              <p className="text-sm text-green-200">
                All dimensions are looking great!
              </p>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
}
