"use client";

import { motion } from "framer-motion";
import { BarChart3, TrendingUp, Users, DollarSign } from "lucide-react";
import { HomePerformance } from "./HomePerformance";
import { LearningInsights } from "./LearningInsights";
import { ContentRecommendations } from "./ContentRecommendations";
import { VideoComparison } from "./VideoComparison";
import { ForecastPanel } from "./ForecastPanel";
import { RecentUploads } from "./RecentUploads";
import { UpcomingPosts } from "./UpcomingPosts";

interface CreatorDashboardProps {
  projectId: string;
}

export function CreatorDashboard({ projectId }: CreatorDashboardProps) {
  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {/* Header */}
      <motion.div
        initial={{ y: -60, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="h-16 border-b border-slate-800 bg-gradient-to-r from-slate-900 to-slate-800/50 flex items-center px-8"
      >
        <h1 className="text-2xl font-semibold">Creator Dashboard</h1>
      </motion.div>

      {/* Main content */}
      <div className="p-8 space-y-8">
        {/* KPI Cards */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="grid grid-cols-4 gap-4"
        >
          <KPICard
            label="Views"
            value="12,450"
            change="+23%"
            icon={TrendingUp}
          />
          <KPICard
            label="Subscribers"
            value="3,240"
            change="+8%"
            icon={Users}
          />
          <KPICard
            label="Watch Time"
            value="48h 32m"
            change="+15%"
            icon={BarChart3}
          />
          <KPICard
            label="Revenue"
            value="$1,234"
            change="+31%"
            icon={DollarSign}
          />
        </motion.div>

        {/* Home Performance */}
        <HomePerformance projectId={projectId} />

        {/* Learning & Recommendations */}
        <div className="grid grid-cols-2 gap-8">
          <LearningInsights projectId={projectId} />
          <ContentRecommendations projectId={projectId} />
        </div>

        {/* Forecast */}
        <ForecastPanel projectId={projectId} />

        {/* Video Comparison */}
        <VideoComparison projectId={projectId} />

        {/* Recent & Upcoming */}
        <div className="grid grid-cols-2 gap-8">
          <RecentUploads projectId={projectId} />
          <UpcomingPosts projectId={projectId} />
        </div>
      </div>
    </div>
  );
}

function KPICard({
  label,
  value,
  change,
  icon: Icon,
}: {
  label: string;
  value: string;
  change: string;
  icon: any;
}) {
  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      className="p-4 rounded-lg border border-slate-700 bg-gradient-to-br from-slate-800 to-slate-900"
    >
      <div className="flex items-start justify-between mb-2">
        <span className="text-xs font-semibold text-slate-400 uppercase">
          {label}
        </span>
        <Icon size={18} className="text-blue-400" />
      </div>
      <div className="text-2xl font-bold text-white mb-1">{value}</div>
      <div className="text-xs text-green-400 font-medium">{change}</div>
    </motion.div>
  );
}
