import { useQuery, useMutation } from "@tanstack/react-query";
import { client } from "./client";

export interface PublishJob {
  id: string;
  render_id: string;
  project_id: string;
  platform_account_id: string;
  platform: string;
  status: string;
  scheduled_time?: string;
  published_at?: string;
  platform_video_id?: string;
  platform_url?: string;
  error_message?: string;
  retry_count: number;
  created_at: string;
  updated_at: string;
}

interface ListPublishJobsParams {
  projectId?: string;
  status?: string;
}

// List publish jobs
export const useListPublishJobs = (params?: ListPublishJobsParams) => {
  return useQuery({
    queryKey: ["publish-jobs", params],
    queryFn: async () => {
      const searchParams = new URLSearchParams();
      if (params?.projectId)
        searchParams.append("project_id", params.projectId);
      if (params?.status) searchParams.append("status", params.status);

      const response = await client.get<PublishJob[]>(
        `/publish/history?${searchParams.toString()}`
      );
      return response.data;
    },
  });
};

// Get single publish job
export const useGetPublishJob = (jobId: string) => {
  return useQuery({
    queryKey: ["publish-job", jobId],
    queryFn: async () => {
      const response = await client.get<PublishJob>(`/publish/${jobId}`);
      return response.data;
    },
    enabled: !!jobId,
  });
};

// Create publish job
export const useCreatePublishJob = () => {
  return useMutation({
    mutationFn: async (data: {
      render_id: string;
      platform_account_id: string;
      platform: string;
      title?: string;
      description?: string;
      tags?: string[];
      caption?: string;
      hashtags?: string[];
      scheduled_time?: string;
    }) => {
      const response = await client.post<PublishJob>("/publish", data);
      return response.data;
    },
  });
};

// Retry publish job
export const useRetryPublishJob = () => {
  return useMutation({
    mutationFn: async (jobId: string) => {
      const response = await client.post<PublishJob>(
        `/publish/${jobId}/retry`,
        { retry: true }
      );
      return response.data;
    },
  });
};

// Cancel publish job
export const useCancelPublishJob = () => {
  return useMutation({
    mutationFn: async (jobId: string) => {
      await client.delete(`/publish/${jobId}`);
      return null;
    },
  });
};

// Connect platform account
export const useConnectPlatform = () => {
  return useMutation({
    mutationFn: async (data: { platform: string; auth_code: string }) => {
      const response = await client.post("/platforms/connect", data, {
        params: { user_id: "current" }, // Replace with actual user ID
      });
      return response.data;
    },
  });
};

// Get platform accounts
export const useGetPlatformAccounts = () => {
  return useQuery({
    queryKey: ["platform-accounts"],
    queryFn: async () => {
      const response = await client.get("/platforms/accounts", {
        params: { user_id: "current" },
      });
      return response.data;
    },
  });
};

// Check platform health
export const usePlatformHealth = (platform: string) => {
  return useQuery({
    queryKey: ["platform-health", platform],
    queryFn: async () => {
      const response = await client.get(`/platforms/health/${platform}`);
      return response.data;
    },
    enabled: !!platform,
  });
};
