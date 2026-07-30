"use client";

import { motion } from "framer-motion";
import { RefreshCw, FileText } from "lucide-react";

interface ReviewHeaderProps {
  projectId: string;
  analysis: any;
}

export default function ReviewHeader({
  projectId,
  analysis,
}: ReviewHeaderProps) {
  return (
    <div className="border-b border-slate-800 bg-gradient-to-r from-slate-900 to-slate-850 backdrop-blur-xl">
      <div className="px-8 py-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-semibold text-white mb-1">
              AI Video Review
            </h1>
            <p className="text-sm text-slate-400">
              Professional optimization analysis
            </p>
          </div>

          <div className="flex items-center gap-3">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-white text-sm font-medium transition-colors flex items-center gap-2"
            >
              <RefreshCw size={16} />
              Analyze Again
            </motion.button>

            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              disabled
              className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <FileText size={16} />
              Generate Edit Plan
            </motion.button>
          </div>
        </div>

        {/* Video Info */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-20 h-20 rounded-lg bg-gradient-to-br from-slate-700 to-slate-800 flex items-center justify-center text-slate-400">
              <img
                src={analysis?.report?.thumbnail || ""}
                alt="Video"
                className="w-full h-full object-cover rounded-lg"
              />
            </div>

            <div>
              <h2 className="text-lg font-semibold text-white">Video Title</h2>
              <div className="flex items-center gap-4 text-sm text-slate-400 mt-1">
                <span>120 seconds</span>
                <span>•</span>
                <span>1920x1080</span>
                <span>•</span>
                <span>Analyzed now</span>
              </div>
            </div>
          </div>

          {/* Overall Score */}
          <div className="flex flex-col items-center gap-2">
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="w-24 h-24 rounded-full bg-gradient-to-br from-blue-600 to-blue-700 flex items-center justify-center"
            >
              <div className="text-center">
                <div className="text-3xl font-bold text-white">
                  {Math.round(analysis?.report?.overall_score || 0)}
                </div>
                <div className="text-xs text-blue-200">Score</div>
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
}
