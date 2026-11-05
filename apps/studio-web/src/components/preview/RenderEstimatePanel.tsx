"use client";

import { motion } from "framer-motion";
import { HardDrive, Zap, Clock, AlertCircle } from "lucide-react";

interface RenderEstimatePanelProps {
  estimate?: any;
}

export function RenderEstimatePanel({ estimate }: RenderEstimatePanelProps) {
  if (!estimate) {
    return (
      <div className="p-4 text-slate-400 text-sm border-b border-slate-800">
        Loading estimate...
      </div>
    );
  }

  const renderTime = Math.round((estimate.estimated_render_time || 0) / 60);
  const outputSize = Math.round(
    (estimate.estimated_output_size || 0) / 1024 / 1024
  );

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="flex-1 border-b border-slate-800 p-4 space-y-4 overflow-y-auto"
    >
      <div>
        <h3 className="text-sm font-semibold text-slate-300 mb-3">
          Render Estimate
        </h3>

        {/* Primary metrics */}
        <div className="space-y-2">
          <div className="flex items-center justify-between p-3 rounded-lg bg-slate-800/50 border border-slate-700">
            <div className="flex items-center gap-2">
              <Clock size={16} className="text-blue-400" />
              <span className="text-sm text-slate-300">Render Time</span>
            </div>
            <span className="font-mono font-semibold text-white">
              {renderTime}m {(estimate.estimated_render_time || 0) % 60}s
            </span>
          </div>

          <div className="flex items-center justify-between p-3 rounded-lg bg-slate-800/50 border border-slate-700">
            <div className="flex items-center gap-2">
              <HardDrive size={16} className="text-green-400" />
              <span className="text-sm text-slate-300">Output Size</span>
            </div>
            <span className="font-mono font-semibold text-white">
              {outputSize}MB
            </span>
          </div>

          <div className="flex items-center justify-between p-3 rounded-lg bg-slate-800/50 border border-slate-700">
            <div className="flex items-center gap-2">
              <Zap size={16} className="text-yellow-400" />
              <span className="text-sm text-slate-300">GPU Usage</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-16 h-1.5 bg-slate-700 rounded-full overflow-hidden">
                <div
                  className="h-full bg-yellow-500"
                  style={{ width: `${estimate.gpu_usage_percent || 0}%` }}
                />
              </div>
              <span className="font-mono text-xs text-slate-400 w-8 text-right">
                {Math.round(estimate.gpu_usage_percent || 0)}%
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Operation breakdown */}
      <div>
        <h3 className="text-xs font-semibold text-slate-400 uppercase mb-2">
          Operation Breakdown
        </h3>
        <div className="space-y-1.5 text-xs">
          <div className="flex justify-between text-slate-400">
            <span>Operations</span>
            <span className="text-white font-medium">
              {estimate.operations_count || 0}
            </span>
          </div>
          <div className="flex justify-between text-slate-400">
            <span>Transitions</span>
            <span className="text-white font-medium">
              {estimate.transitions_count || 0}
            </span>
          </div>
          <div className="flex justify-between text-slate-400">
            <span>Captions</span>
            <span className="text-white font-medium">
              {estimate.captions_count || 0}
            </span>
          </div>
          <div className="flex justify-between text-slate-400">
            <span>Effects</span>
            <span className="text-white font-medium">
              {estimate.effects_count || 0}
            </span>
          </div>
        </div>
      </div>

      {/* Storage estimate */}
      <motion.div
        className="p-3 rounded-lg bg-blue-900/30 border border-blue-700/50"
        whileHover={{ borderColor: "#3b82f6" }}
      >
        <p className="text-xs text-blue-300 mb-1 flex items-center gap-2">
          <AlertCircle size={14} />
          Storage Required
        </p>
        <p className="text-sm font-semibold text-blue-200">{outputSize}MB</p>
      </motion.div>
    </motion.div>
  );
}
