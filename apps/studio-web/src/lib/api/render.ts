import { useQuery, useMutation } from "@tanstack/react-query";
import { client } from "./client";

export interface RenderLog {
  id: string;
  stage: string;
  status: string;
  message?: string;
  progress?: number;
  timestamp: string;
}

export interface Render {
  id: string;
  project_id: string;
  preview_id: string;
  edit_plan_id: string;
  status: string;
  quality: string;
  platform?: string;
  priority: number;
  output_path?: string;
  output_size?: number;
  duration?: number;
  fps?: number;
  resolution?: string;
  codec?: string;
  started_at?: string;
  completed_at?: string;
  estimated_time?: number;
  elapsed_time: number;
  progress_percent: number;
  current_stage?: string;
  error_message?: string;
  retry_count: number;
  created_at: string;
  updated_at: string;
}

interface ListRendersParams {
  projectId?: string;
  status?: string;
}

// List renders
export const useListRenders = (params?: ListRendersParams) => {
  return useQuery({
    queryKey: ["renders", params],
    queryFn: async () => {
      const searchParams = new URLSearchParams();
      if (params?.projectId)
        searchParams.append("project_id", params.projectId);
      if (params?.status) searchParams.append("status", params.status);

      const response = await client.get<Render[]>(
        `/renders?${searchParams.toString()}`
      );
      return response.data;
    },
  });
};

// Get single render
export const useGetRender = (renderId: string) => {
  return useQuery({
    queryKey: ["render", renderId],
    queryFn: async () => {
      const response = await client.get<Render>(`/renders/${renderId}`);
      return response.data;
    },
    enabled: !!renderId,
  });
};

// Get render logs
export const useGetRenderLogs = (renderId: string) => {
  return useQuery({
    queryKey: ["render-logs", renderId],
    queryFn: async () => {
      const response = await client.get<RenderLog[]>(
        `/renders/${renderId}/logs`
      );
      return response.data;
    },
    enabled: !!renderId,
  });
};

// Start render
export const useStartRender = () => {
  return useMutation({
    mutationFn: async ({
      projectId,
      quality,
      platform,
    }: {
      projectId: string;
      quality: string;
      platform?: string;
    }) => {
      const response = await client.post<Render>(
        `/projects/${projectId}/render`,
        { quality, platform }
      );
      return response.data;
    },
  });
};

// Cancel render
export const useCancelRender = () => {
  return useMutation({
    mutationFn: async (renderId: string) => {
      const response = await client.post<Render>(
        `/renders/${renderId}/cancel`,
        { cancel: true }
      );
      return response.data;
    },
  });
};

// Retry render
export const useRetryRender = () => {
  return useMutation({
    mutationFn: async (renderId: string) => {
      const response = await client.post<Render>(`/renders/${renderId}/retry`, {
        retry: true,
      });
      return response.data;
    },
  });
};
