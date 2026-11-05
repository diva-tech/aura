import { useQuery, useMutation } from "@tanstack/react-query";
import { client } from "./client";

export interface RenderSettings {
  id: string;
  project_id: string;
  resolution: string;
  fps: number;
  codec: string;
  bitrate: string;
  platform?: string;
  audio_bitrate: string;
  audio_codec: string;
  quality_level: number;
  created_at: string;
  updated_at: string;
}

export interface RenderEstimate {
  id: string;
  project_id: string;
  edit_plan_id: string;
  estimated_duration?: number;
  estimated_render_time?: number;
  estimated_output_size?: number;
  gpu_usage_percent?: number;
  cpu_usage_percent?: number;
  operations_count: number;
  effects_count: number;
  captions_count: number;
  transitions_count: number;
  created_at: string;
}

export interface Preview {
  id: string;
  project_id: string;
  edit_plan_id: string;
  version: number;
  status: string;
  quality: string;
  approved: boolean;
  file_path?: string;
  duration?: number;
  filesize?: number;
  estimated_render_time?: number;
  estimated_output_size?: number;
  created_at: string;
  updated_at: string;
}

// Fetch preview for project
export const usePreview = (projectId: string) => {
  return useQuery({
    queryKey: ["preview", projectId],
    queryFn: async () => {
      const response = await client.get<Preview>(
        `/projects/${projectId}/preview`
      );
      return response.data;
    },
    enabled: !!projectId,
  });
};

// Generate preview
export const useGeneratePreview = () => {
  return useMutation({
    mutationFn: async ({
      projectId,
      quality,
    }: {
      projectId: string;
      quality: string;
    }) => {
      const response = await client.post<Preview>(
        `/projects/${projectId}/preview`,
        { quality }
      );
      return response.data;
    },
  });
};

// Approve preview
export const useApprovePreview = () => {
  return useMutation({
    mutationFn: async (previewId: string) => {
      const response = await client.post<Preview>(
        `/preview/${previewId}/approve`,
        { approved: true }
      );
      return response.data;
    },
  });
};

// Fetch render estimate
export const useRenderEstimate = (projectId: string) => {
  return useQuery({
    queryKey: ["render-estimate", projectId],
    queryFn: async () => {
      const response = await client.get<RenderEstimate>(
        `/projects/${projectId}/render-estimate`
      );
      return response.data;
    },
    enabled: !!projectId,
  });
};

// Update render settings
export const useUpdateRenderSettings = () => {
  return useMutation({
    mutationFn: async ({
      projectId,
      settings,
    }: {
      projectId: string;
      settings: Partial<RenderSettings>;
    }) => {
      const response = await client.put<RenderSettings>(
        `/projects/${projectId}/render-settings`,
        settings
      );
      return response.data;
    },
  });
};

// Add preview comment
export const useAddPreviewComment = () => {
  return useMutation({
    mutationFn: async ({
      previewId,
      timestamp,
      text,
      author,
    }: {
      previewId: string;
      timestamp: number;
      text: string;
      author?: string;
    }) => {
      const response = await client.post(`/preview/${previewId}/comments`, {
        timestamp,
        text,
        author,
      });
      return response.data;
    },
  });
};
