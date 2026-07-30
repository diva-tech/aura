"use client";

import { motion } from "framer-motion";
import { CheckCircle, AlertCircle } from "lucide-react";

interface Platform {
  name: string;
  status: "healthy" | "degraded" | "down";
  responseTime?: number;
}

export function PlatformHealthDashboard() {
  const platforms: Platform[] = [
    { name: "YouTube", status: "healthy", responseTime: 120 },
    { name: "Instagram", status: "healthy", responseTime: 150 },
    { name: "TikTok", status: "healthy", responseTime: 180 },
    { name: "LinkedIn", status: "healthy", responseTime: 130 },
    { name: "Podcast", status: "healthy", responseTime: 100 },
  ];

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-4"
    >
      <div>
        <h3 className="text-sm font-semibold text-slate-300 mb-3">
          Platform Status
        </h3>

        <div className="space-y-2">
          {platforms.map((platform) => (
            <div
              key={platform.name}
              className="flex items-center justify-between p-3 rounded-lg bg-slate-800/50 border border-slate-700"
            >
              <div className="flex items-center gap-2">
                {platform.status === "healthy" ? (
                  <CheckCircle size={16} className="text-green-400" />
                ) : (
                  <AlertCircle size={16} className="text-yellow-400" />
                )}
                <span className="text-sm text-slate-300">{platform.name}</span>
              </div>
              {platform.responseTime && (
                <span className="text-xs text-slate-500">
                  {platform.responseTime}ms
                </span>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* System Status */}
      <motion.div className="p-3 rounded-lg bg-green-900/20 border border-green-700/50">
        <p className="text-xs text-green-300 mb-1">System Status</p>
        <p className="text-sm font-semibold text-green-200">
          All Systems Operational
        </p>
      </motion.div>

      {/* Publishing Stats */}
      <div className="p-3 rounded-lg bg-slate-800/50 border border-slate-700">
        <h4 className="text-xs font-semibold text-slate-300 mb-2">
          Publishing Stats
        </h4>
        <div className="space-y-1 text-xs text-slate-400">
          <div className="flex justify-between">
            <span>Today</span>
            <span className="text-white">5 published</span>
          </div>
          <div className="flex justify-between">
            <span>This Week</span>
            <span className="text-white">28 published</span>
          </div>
          <div className="flex justify-between">
            <span>Success Rate</span>
            <span className="text-green-400">99.5%</span>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
