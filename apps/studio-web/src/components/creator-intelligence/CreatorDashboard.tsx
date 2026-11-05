"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import {
  useCreatorBrief,
  useCreatorInsights,
  useContentOpportunities,
  useVideoHealthScore,
  usePerformancePrediction,
  useExplanations,
  useThumbnailInsight,
} from "@/lib/api/creator-intelligence";
import { CreatorBriefCard } from "./CreatorBriefCard";
import { ExplainabilityPanel } from "./ExplainabilityPanel";
import { InsightsFeed } from "./InsightsFeed";
import { VideoHealthScore as VideoHealthScoreComponent } from "./VideoHealthScore";
import { AlertCircle, Loader2, TrendingUp } from "lucide-react";
import {
  transformCreatorBrief,
  transformHealthScore,
} from "@/lib/transformers/creator-intelligence";

interface CreatorDashboardProps {
  projectId: string;
}

export function CreatorDashboard({ projectId }: CreatorDashboardProps) {
  const [selectedExplanation, setSelectedExplanation] = useState<string | null>(
    null
  );

  const {
    data: brief,
    isLoading: briefLoading,
    error: briefError,
  } = useCreatorBrief(projectId);
  const { data: insights, isLoading: insightsLoading } =
    useCreatorInsights(projectId);
  const { data: opportunities, isLoading: opportunitiesLoading } =
    useContentOpportunities(projectId);
  const { data: healthScore, isLoading: healthLoading } =
    useVideoHealthScore(projectId);
  const { data: prediction, isLoading: predictionLoading } =
    usePerformancePrediction(projectId);
  const { data: explanations, isLoading: explanationsLoading } =
    useExplanations(projectId);
  const { data: thumbnailInsight, isLoading: thumbnailLoading } =
    useThumbnailInsight(projectId);

  if (briefLoading || insightsLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 size={32} className="text-blue-400 animate-spin" />
      </div>
    );
  }

  if (briefError) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="p-6 rounded-lg border border-red-700/50 bg-red-950/20"
      >
        <div className="flex items-center gap-3">
          <AlertCircle size={20} className="text-red-400" />
          <div>
            <h3 className="font-semibold text-red-300">Error Loading Brief</h3>
            <p className="text-sm text-red-200">
              Failed to load creator brief. Please try again.
            </p>
          </div>
        </div>
      </motion.div>
    );
  }

  const briefData = brief ? transformCreatorBrief(brief) : null;
  const healthData = healthScore ? transformHealthScore(healthScore) : null;

  const selectedExp = explanations?.find(
    (exp) => exp.id === selectedExplanation
  );

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-8"
    >
      {/* Creator Brief */}
      {briefData && (
        <div className="space-y-4">
          <h1 className="text-2xl font-bold text-white">Today's Brief</h1>
          <CreatorBriefCard {...briefData} />
        </div>
      )}

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Insights */}
        <div className="lg:col-span-2 space-y-6">
          {/* Insights Feed */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-4"
          >
            <div className="flex items-center gap-2">
              <TrendingUp size={20} className="text-blue-400" />
              <h2 className="text-lg font-bold text-white">AI Insights</h2>
            </div>
            {insightsLoading ? (
              <div className="flex justify-center py-6">
                <Loader2 size={24} className="text-blue-400 animate-spin" />
              </div>
            ) : insights && insights.length > 0 ? (
              <InsightsFeed
                insights={insights.map((i) => ({
                  id: i.id,
                  type: (i.insight_type as any) || "trend",
                  title: i.title,
                  description: i.description,
                  confidence: i.confidence,
                  source: i.data_source || "AI",
                  actionable: i.actionable === "pending",
                }))}
              />
            ) : (
              <div className="p-6 text-center rounded-lg border border-slate-700 bg-slate-800/20">
                <p className="text-slate-400">No insights yet</p>
              </div>
            )}
          </motion.div>

          {/* Explanability Panel */}
          {selectedExp && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <ExplainabilityPanel
                operation={selectedExp.operation}
                reason={selectedExp.reason}
                confidence={selectedExp.confidence}
                expectedImprovement={
                  selectedExp.expected_improvement
                    ? JSON.parse(selectedExp.expected_improvement)
                    : []
                }
                dataSources={
                  selectedExp.data_sources
                    ? JSON.parse(selectedExp.data_sources)
                    : []
                }
                alternatives={
                  selectedExp.alternatives
                    ? JSON.parse(selectedExp.alternatives)
                    : []
                }
              />
            </motion.div>
          )}
        </div>

        {/* Right Column - Scores & Predictions */}
        <div className="space-y-6">
          {/* Health Score */}
          {healthData && !healthLoading && (
            <VideoHealthScoreComponent {...healthData} />
          )}

          {/* Performance Prediction */}
          {prediction && !predictionLoading && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="p-6 rounded-lg border border-slate-700 bg-slate-800/30 space-y-4"
            >
              <h3 className="font-semibold text-white">Performance Forecast</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-slate-400">
                    Predicted Views
                  </span>
                  <span className="font-bold text-white">
                    {prediction.predicted_views.toLocaleString()}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-slate-400">Predicted CTR</span>
                  <span className="font-bold text-white">
                    {prediction.predicted_ctr_pct.toFixed(1)}%
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-slate-400">
                    Predicted Revenue
                  </span>
                  <span className="font-bold text-green-400">
                    ₹{prediction.predicted_revenue.toLocaleString()}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-slate-400">Confidence</span>
                  <span className="font-bold text-blue-400">
                    {(prediction.confidence * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
            </motion.div>
          )}

          {/* Content Opportunities */}
          {opportunities &&
            opportunities.length > 0 &&
            !opportunitiesLoading && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="p-6 rounded-lg border border-slate-700 bg-slate-800/30 space-y-4"
              >
                <h3 className="font-semibold text-white">Top Opportunities</h3>
                <div className="space-y-2">
                  {opportunities.slice(0, 3).map((opp) => (
                    <div
                      key={opp.id}
                      className="p-3 rounded-lg bg-slate-900/50 hover:bg-slate-900 transition-colors cursor-pointer"
                    >
                      <p className="text-sm font-medium text-white">
                        {opp.title}
                      </p>
                      <p className="text-xs text-slate-400 mt-1">
                        Demand: {opp.demand_score.toFixed(0)}%
                      </p>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}

          {/* Thumbnail Insight */}
          {thumbnailInsight && !thumbnailLoading && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="p-6 rounded-lg border border-slate-700 bg-slate-800/30 space-y-4"
            >
              <h3 className="font-semibold text-white">Thumbnail Health</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-slate-400">CTR Prediction</span>
                  <span className="font-bold text-white">
                    {thumbnailInsight.ctr_prediction.toFixed(1)}%
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-slate-400">Visual Clarity</span>
                  <span className="font-bold text-blue-400">
                    {thumbnailInsight.visual_complexity_score.toFixed(0)}/100
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-slate-400">Brand Match</span>
                  <span className="font-bold text-green-400">
                    {thumbnailInsight.brand_consistency_score.toFixed(0)}/100
                  </span>
                </div>
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </motion.div>
  );
}
