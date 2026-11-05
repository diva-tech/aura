import { CreatorBriefCard } from "@/components/creator-intelligence/CreatorBriefCard";
import { VideoHealthScore } from "@/components/creator-intelligence/VideoHealthScore";

export interface CreatorBriefData {
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

export interface VideoHealthScoreData {
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

export function transformCreatorBrief(apiResponse: any): CreatorBriefData {
  const pendingTasks = apiResponse.pending_tasks
    ? JSON.parse(apiResponse.pending_tasks)
    : [];
  const riskAlerts = apiResponse.risk_alerts
    ? JSON.parse(apiResponse.risk_alerts).map(
        (alert: any) => alert.type || "Unknown risk"
      )
    : [];

  return {
    views: apiResponse.yesterday_views || 0,
    viewsChange: apiResponse.yesterday_views_change_pct || 0,
    subscribers: apiResponse.yesterday_subscribers || 0,
    revenue: apiResponse.yesterday_revenue || 0,
    watchTime: apiResponse.yesterday_watch_time_minutes || 0,
    retention: apiResponse.yesterday_retention_pct || 0,
    ctr: apiResponse.yesterday_ctr_pct || 0,
    topOpportunity: apiResponse.top_opportunity || "No opportunities yet",
    bestUploadTime: apiResponse.best_upload_time || "19:00",
    pendingTasks,
    riskAlerts,
  };
}

export function transformHealthScore(apiResponse: any): VideoHealthScoreData {
  const recommendations = apiResponse.recommendations
    ? JSON.parse(apiResponse.recommendations)
    : [];

  return {
    overallScore: apiResponse.overall_score || 0,
    hookScore: apiResponse.hook_score || 0,
    retentionScore: apiResponse.retention_score || 0,
    editingScore: apiResponse.editing_score || 0,
    captionsScore: apiResponse.captions_score || 0,
    thumbnailScore: apiResponse.thumbnail_score || 0,
    seoScore: apiResponse.seo_score || 0,
    ctaScore: apiResponse.cta_score || 0,
    storytellingScore: apiResponse.storytelling_score || 0,
    pacingScore: apiResponse.pacing_score || 0,
    brandConsistencyScore: apiResponse.brand_consistency_score || 0,
    recommendations,
  };
}
