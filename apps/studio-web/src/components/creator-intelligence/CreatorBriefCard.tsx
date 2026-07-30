"use client";

import { motion } from "framer-motion";
import {
  TrendingUp,
  Users,
  DollarSign,
  Eye,
  Zap,
  AlertCircle,
} from "lucide-react";

interface CreatorBriefProps {
  views: number;
  viewsChange: number;
  subscribers: number;
  revenue: number;
  watchTime: number;
  retention: number;
  ctr: number;
  topOpportunity: string;
  bestUploadTime: string;
  pendingTasks: string[];
  riskAlerts: string[];
}

export function CreatorBriefCard({
  views,
  viewsChange,
  subscribers,
  revenue,
  watchTime,
  retention,
  ctr,
  topOpportunity,
  bestUploadTime,
  pendingTasks,
  riskAlerts,
}: CreatorBriefProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      {/* Greeting */}
      <div className="p-6 rounded-lg border border-slate-700 bg-gradient-to-r from-slate-800/50 to-slate-900/50">
        <h1 className="text-2xl font-bold text-white mb-2">Good Morning.</h1>
        <p className="text-slate-400">
          Here's your personalized briefing for today
        </p>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <motion.div
          whileHover={{ scale: 1.02 }}
          className="p-4 rounded-lg border border-slate-700 bg-slate-800/30"
        >
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm text-slate-400">Views</p>
            <Eye size={18} className="text-blue-400" />
          </div>
          <p className="text-2xl font-bold text-white">{views}</p>
          <p className="text-xs text-green-400">+{viewsChange.toFixed(1)}%</p>
        </motion.div>

        <motion.div
          whileHover={{ scale: 1.02 }}
          className="p-4 rounded-lg border border-slate-700 bg-slate-800/30"
        >
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm text-slate-400">Subscribers</p>
            <Users size={18} className="text-purple-400" />
          </div>
          <p className="text-2xl font-bold text-white">+{subscribers}</p>
          <p className="text-xs text-slate-500">Yesterday</p>
        </motion.div>

        <motion.div
          whileHover={{ scale: 1.02 }}
          className="p-4 rounded-lg border border-slate-700 bg-slate-800/30"
        >
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm text-slate-400">Revenue</p>
            <DollarSign size={18} className="text-green-400" />
          </div>
          <p className="text-2xl font-bold text-white">₹{revenue}</p>
          <p className="text-xs text-slate-500">Yesterday</p>
        </motion.div>

        <motion.div
          whileHover={{ scale: 1.02 }}
          className="p-4 rounded-lg border border-slate-700 bg-slate-800/30"
        >
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm text-slate-400">Retention</p>
            <TrendingUp size={18} className="text-orange-400" />
          </div>
          <p className="text-2xl font-bold text-white">{retention}%</p>
          <p className="text-xs text-slate-500">Average</p>
        </motion.div>
      </div>

      {/* AI Learned Section */}
      <motion.div
        whileHover={{ scale: 1.01 }}
        className="p-6 rounded-lg border border-slate-700 bg-slate-800/20 border-l-4 border-l-blue-500"
      >
        <div className="flex items-start gap-3">
          <Zap size={20} className="text-blue-400 mt-1 flex-shrink-0" />
          <div>
            <h3 className="font-semibold text-white mb-1">AI Learned</h3>
            <p className="text-slate-300">
              Videos under 8 minutes performed 19% better with your audience.
            </p>
          </div>
        </div>
      </motion.div>

      {/* Today's Opportunity */}
      <motion.div
        whileHover={{ scale: 1.01 }}
        className="p-6 rounded-lg border border-slate-700 bg-slate-800/20 border-l-4 border-l-green-500"
      >
        <div className="flex items-start gap-3">
          <TrendingUp size={20} className="text-green-400 mt-1 flex-shrink-0" />
          <div>
            <h3 className="font-semibold text-white mb-1">
              Today's Opportunity
            </h3>
            <p className="text-slate-300 mb-2">{topOpportunity}</p>
            <p className="text-xs text-slate-500">Demand Score: 82%</p>
          </div>
        </div>
      </motion.div>

      {/* Best Upload Time */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <motion.div
          whileHover={{ scale: 1.01 }}
          className="p-6 rounded-lg border border-slate-700 bg-slate-800/20"
        >
          <h3 className="text-sm font-semibold text-slate-400 mb-3">
            Best Upload Time
          </h3>
          <p className="text-3xl font-bold text-white mb-1">{bestUploadTime}</p>
          <p className="text-xs text-slate-500">Today (8.3% CTR avg)</p>
        </motion.div>

        <motion.div
          whileHover={{ scale: 1.01 }}
          className="p-6 rounded-lg border border-slate-700 bg-slate-800/20"
        >
          <h3 className="text-sm font-semibold text-slate-400 mb-3">
            Key Metrics
          </h3>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-slate-400">Watch Time</span>
              <span className="text-white font-medium">
                {watchTime.toLocaleString()} min
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-slate-400">CTR</span>
              <span className="text-white font-medium">{ctr}%</span>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Suggested Actions */}
      <motion.div
        whileHover={{ scale: 1.01 }}
        className="p-6 rounded-lg border border-slate-700 bg-slate-800/20"
      >
        <h3 className="font-semibold text-white mb-4">Suggested Actions</h3>
        <div className="space-y-2">
          {pendingTasks.map((task, idx) => (
            <motion.div
              key={idx}
              className="flex items-center gap-3 p-3 rounded-lg bg-slate-900/50 hover:bg-slate-900 transition-colors"
            >
              <div className="w-2 h-2 rounded-full bg-blue-400" />
              <p className="text-sm text-slate-300">{task}</p>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Risk Alerts */}
      {riskAlerts.length > 0 && (
        <motion.div
          whileHover={{ scale: 1.01 }}
          className="p-6 rounded-lg border border-amber-700/50 bg-amber-950/20"
        >
          <div className="flex items-start gap-3">
            <AlertCircle
              size={20}
              className="text-amber-400 mt-1 flex-shrink-0"
            />
            <div>
              <h3 className="font-semibold text-amber-300 mb-2">Risk Alerts</h3>
              <div className="space-y-1">
                {riskAlerts.map((alert, idx) => (
                  <p key={idx} className="text-sm text-amber-200">
                    {alert}
                  </p>
                ))}
              </div>
            </div>
          </div>
        </motion.div>
      )}
    </motion.div>
  );
}
