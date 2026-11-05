"use client";

import { motion } from "framer-motion";
import { Activity, Zap, HardDrive } from "lucide-react";

interface GPUMonitoringProps {
  currentRender?: any;
}

export function GPUMonitoring({ currentRender }: GPUMonitoringProps) {
  const mockMetrics = {
    gpuUsage: 75,
    cpuUsage: 45,
    memoryUsage: 58,
    temperature: 62,
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-4"
    >
      <div>
        <h3 className="text-sm font-semibold text-slate-300 mb-3">
          System Resources
        </h3>

        {/* GPU */}
        <div className="p-3 rounded-lg bg-slate-800/50 border border-slate-700 mb-2">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <Zap size={16} className="text-yellow-400" />
              <span className="text-xs font-medium text-slate-300">GPU</span>
            </div>
            <span className="text-sm font-semibold text-white">
              {mockMetrics.gpuUsage}%
            </span>
          </div>
          <div className="w-full h-2 bg-slate-700 rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-yellow-500"
              initial={{ width: "0%" }}
              animate={{ width: `${mockMetrics.gpuUsage}%` }}
              transition={{ duration: 0.5 }}
            />
          </div>
        </div>

        {/* CPU */}
        <div className="p-3 rounded-lg bg-slate-800/50 border border-slate-700 mb-2">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <Activity size={16} className="text-blue-400" />
              <span className="text-xs font-medium text-slate-300">CPU</span>
            </div>
            <span className="text-sm font-semibold text-white">
              {mockMetrics.cpuUsage}%
            </span>
          </div>
          <div className="w-full h-2 bg-slate-700 rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-blue-500"
              initial={{ width: "0%" }}
              animate={{ width: `${mockMetrics.cpuUsage}%` }}
              transition={{ duration: 0.5 }}
            />
          </div>
        </div>

        {/* Memory */}
        <div className="p-3 rounded-lg bg-slate-800/50 border border-slate-700">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <HardDrive size={16} className="text-green-400" />
              <span className="text-xs font-medium text-slate-300">Memory</span>
            </div>
            <span className="text-sm font-semibold text-white">
              {mockMetrics.memoryUsage}%
            </span>
          </div>
          <div className="w-full h-2 bg-slate-700 rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-green-500"
              initial={{ width: "0%" }}
              animate={{ width: `${mockMetrics.memoryUsage}%` }}
              transition={{ duration: 0.5 }}
            />
          </div>
        </div>
      </div>

      {/* Temperature */}
      <motion.div className="p-3 rounded-lg bg-orange-900/20 border border-orange-700/50">
        <p className="text-xs text-orange-300 mb-1">GPU Temperature</p>
        <p className="text-2xl font-bold text-orange-200">
          {mockMetrics.temperature}°C
        </p>
        <p className="text-xs text-orange-300 mt-1">Normal operating range</p>
      </motion.div>

      {/* Queue Status */}
      {currentRender && (
        <motion.div className="p-3 rounded-lg bg-blue-900/20 border border-blue-700/50">
          <p className="text-xs text-blue-300 mb-2">Active Jobs</p>
          <div className="space-y-1">
            <div className="flex items-center justify-between text-xs">
              <span className="text-blue-300">Processing</span>
              <span className="text-white font-medium">1</span>
            </div>
            <div className="flex items-center justify-between text-xs">
              <span className="text-blue-300">Queued</span>
              <span className="text-white font-medium">0</span>
            </div>
          </div>
        </motion.div>
      )}
    </motion.div>
  );
}
