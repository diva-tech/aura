import { useQuery } from "@tanstack/react-query";
import { client } from "./client";

interface CreatorProfile {
  id: string;
  project_id: string;
  preferred_editing_style?: string;
  preferred_upload_schedule?: string;
  preferred_platforms?: string;
  typical_video_duration?: number;
  audience_profile?: string;
  publishing_frequency?: string;
  favorite_thumbnail_style?: string;
  favorite_hook_style?: string;
  learning_confidence: number;
  accepted_suggestions: number;
  rejected_suggestions: number;
  created_at: string;
  updated_at: string;
}

interface CreatorBrief {
  id: string;
  project_id: string;
  brief_date: string;
  yesterday_views: number;
  yesterday_views_change_pct: number;
  yesterday_subscribers: number;
  yesterday_revenue: number;
  yesterday_watch_time_minutes: number;
  yesterday_retention_pct: number;
  yesterday_ctr_pct: number;
  best_performing_video_id?: string;
  worst_performing_video_id?: string;
  top_opportunity?: string;
  best_upload_time?: string;
  pending_tasks?: string;
  risk_alerts?: string;
  created_at: string;
}

interface CreatorInsight {
  id: string;
  project_id: string;
  insight_type: string;
  title: string;
  description: string;
  data_source?: string;
  confidence: number;
  actionable: string;
  metadata?: string;
  created_at: string;
  updated_at: string;
}

interface AIExplanation {
  id: string;
  project_id: string;
  subject_type: string;
  subject_id?: string;
  operation: string;
  reason: string;
  confidence: number;
  expected_improvement?: string;
  data_sources?: string;
  alternatives?: string;
  created_at: string;
}

interface PerformancePrediction {
  id: string;
  project_id: string;
  video_id?: string;
  predicted_views: number;
  predicted_ctr_pct: number;
  predicted_watch_time_minutes: number;
  predicted_revenue: number;
  audience_match_pct: number;
  upload_score: number;
  confidence: number;
  reasoning?: string;
  created_at: string;
}

interface VideoHealthScore {
  id: string;
  project_id: string;
  video_id?: string;
  overall_score: number;
  hook_score: number;
  retention_score: number;
  editing_score: number;
  captions_score: number;
  thumbnail_score: number;
  seo_score: number;
  cta_score: number;
  storytelling_score: number;
  pacing_score: number;
  brand_consistency_score: number;
  recommendations?: string;
  created_at: string;
  updated_at: string;
}

interface ContentOpportunity {
  id: string;
  project_id: string;
  opportunity_type: string;
  title: string;
  description: string;
  demand_score: number;
  competition_level?: string;
  expected_views: number;
  data_source?: string;
  metadata?: string;
  created_at: string;
}

interface ThumbnailInsight {
  id: string;
  project_id: string;
  video_id?: string;
  ctr_prediction: number;
  visual_complexity_score: number;
  text_contrast_score: number;
  face_detection?: string;
  emotion_score: number;
  brand_consistency_score: number;
  improvement_suggestions?: string;
  created_at: string;
}

export const useCreatorProfile = (projectId: string) => {
  return useQuery({
    queryKey: ["creator", projectId, "profile"],
    queryFn: async () => {
      const response = await client.get<CreatorProfile>(
        `/creator/${projectId}/profile`
      );
      return response.data;
    },
  });
};

export const useCreatorBrief = (projectId: string) => {
  return useQuery({
    queryKey: ["creator", projectId, "brief"],
    queryFn: async () => {
      const response = await client.get<CreatorBrief>(
        `/creator/${projectId}/brief`
      );
      return response.data;
    },
  });
};

export const useCreatorInsights = (
  projectId: string,
  insightType?: string,
  limit: number = 10
) => {
  return useQuery({
    queryKey: ["creator", projectId, "insights", insightType],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (insightType) params.append("insight_type", insightType);
      params.append("limit", limit.toString());

      const response = await client.get<CreatorInsight[]>(
        `/creator/${projectId}/insights?${params}`
      );
      return response.data;
    },
  });
};

export const useContentOpportunities = (
  projectId: string,
  limit: number = 10
) => {
  return useQuery({
    queryKey: ["creator", projectId, "opportunities"],
    queryFn: async () => {
      const response = await client.get<ContentOpportunity[]>(
        `/creator/${projectId}/opportunities?limit=${limit}`
      );
      return response.data;
    },
  });
};

export const useVideoHealthScore = (projectId: string) => {
  return useQuery({
    queryKey: ["creator", projectId, "health"],
    queryFn: async () => {
      const response = await client.get<VideoHealthScore>(
        `/creator/${projectId}/health`
      );
      return response.data;
    },
  });
};

export const usePerformancePrediction = (projectId: string) => {
  return useQuery({
    queryKey: ["creator", projectId, "prediction"],
    queryFn: async () => {
      const response = await client.get<PerformancePrediction>(
        `/creator/${projectId}/prediction`
      );
      return response.data;
    },
  });
};

export const useExplanations = (
  projectId: string,
  subjectType?: string,
  limit: number = 10
) => {
  return useQuery({
    queryKey: ["creator", projectId, "explanations", subjectType],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (subjectType) params.append("subject_type", subjectType);
      params.append("limit", limit.toString());

      const response = await client.get<AIExplanation[]>(
        `/creator/${projectId}/explanations?${params}`
      );
      return response.data;
    },
  });
};

export const useThumbnailInsight = (projectId: string) => {
  return useQuery({
    queryKey: ["creator", projectId, "thumbnail"],
    queryFn: async () => {
      const response = await client.get<ThumbnailInsight>(
        `/creator/${projectId}/thumbnail`
      );
      return response.data;
    },
  });
};

export const useCreatorContext = (projectId: string) => {
  return useQuery({
    queryKey: ["creator", projectId, "context"],
    queryFn: async () => {
      const response = await client.get(`/creator/${projectId}/context`);
      return response.data;
    },
  });
};
