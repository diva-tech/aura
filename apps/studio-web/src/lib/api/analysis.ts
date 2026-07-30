import { useQuery, useMutation } from "@tanstack/react-query";
import { client } from "./client";

export interface AnalysisReport {
  id: string;
  project_id: string;
  video_id: string;
  status: "pending" | "analyzing" | "completed" | "failed";
  overall_score: number;
  viral_score: number;
  engagement_score: number;
  hook_score: number;
  retention_score: number;
  clarity_score: number;
  audio_score: number;
  visual_score: number;
  summary: string;
  created_at: string;
  updated_at: string;
}

export interface Scene {
  id: string;
  report_id: string;
  start_time: number;
  end_time: number;
  summary: string;
  emotion: string;
  importance: number;
  objects: any[];
  created_at: string;
  updated_at: string;
}

export interface Transcript {
  id: string;
  report_id: string;
  start_time: number;
  end_time: number;
  text: string;
  speaker: string;
  confidence: number;
  created_at: string;
  updated_at: string;
}

export interface Suggestion {
  id: string;
  report_id: string;
  type: string;
  title: string;
  description: string;
  reason: string;
  severity: "high" | "medium" | "low";
  confidence: number;
  accepted: boolean;
  estimated_impact: number;
  created_at: string;
  updated_at: string;
}

export interface VideoMetrics {
  id: string;
  report_id: string;
  duration: number;
  fps: number;
  bitrate: string;
  resolution: string;
  codec: string;
  audio_level: number;
  silence_percentage: number;
  scene_count: number;
  face_count: number;
  speech_rate: number;
  text_coverage: number;
  music_percentage: number;
  created_at: string;
  updated_at: string;
}

export interface AnalysisDetail {
  report: AnalysisReport;
  metrics: VideoMetrics;
  scenes: Scene[];
  transcript: Transcript[];
  suggestions: Suggestion[];
}

// Fetch full analysis report
export const useAnalysisReport = (projectId: string) => {
  return useQuery({
    queryKey: ["analysis", projectId],
    queryFn: async () => {
      const response = await client.get<AnalysisDetail>(
        `/projects/${projectId}/analysis`
      );
      return response.data;
    },
    enabled: !!projectId,
  });
};

// Fetch analysis status
export const useAnalysisStatus = (projectId: string) => {
  return useQuery({
    queryKey: ["analysis-status", projectId],
    queryFn: async () => {
      const response = await client.get<{ status: string }>(
        `/projects/${projectId}/analysis`
      );
      return response.data;
    },
    enabled: !!projectId,
    refetchInterval: (data) => {
      if (data?.status === "completed") return false;
      return 2000;
    },
  });
};

// Fetch suggestions
export const useSuggestions = (projectId: string) => {
  return useQuery({
    queryKey: ["suggestions", projectId],
    queryFn: async () => {
      const response = await client.get<Suggestion[]>(
        `/projects/${projectId}/suggestions`
      );
      return response.data;
    },
    enabled: !!projectId,
  });
};

// Fetch transcript
export const useTranscript = (projectId: string) => {
  return useQuery({
    queryKey: ["transcript", projectId],
    queryFn: async () => {
      const response = await client.get<Transcript[]>(
        `/projects/${projectId}/transcript`
      );
      return response.data;
    },
    enabled: !!projectId,
  });
};

// Accept suggestion
export const useAcceptSuggestion = () => {
  return useMutation({
    mutationFn: async ({
      projectId,
      suggestionId,
    }: {
      projectId: string;
      suggestionId: string;
    }) => {
      const response = await client.post(
        `/projects/${projectId}/suggestions/${suggestionId}/accept`
      );
      return response.data;
    },
  });
};

// Trigger analysis
export const useAnalyzeVideo = () => {
  return useMutation({
    mutationFn: async (projectId: string) => {
      const response = await client.post<AnalysisReport>(
        `/projects/${projectId}/analyze`
      );
      return response.data;
    },
  });
};
