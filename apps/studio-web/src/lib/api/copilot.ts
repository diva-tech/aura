import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { client } from "./client";

interface CopilotMessage {
  id: string;
  project_id: string;
  role: "user" | "assistant";
  message: string;
  context?: string;
  created_at: string;
}

interface CopilotChatRequest {
  message: string;
  context?: Record<string, any>;
}

interface CopilotChatResponse {
  user_message: CopilotMessage;
  assistant_message: CopilotMessage;
  orchestration_context?: Record<string, any>;
}

interface CopilotMemory {
  id: string;
  project_id: string;
  memory_type: string;
  key: string;
  value: string;
  created_at: string;
  updated_at: string;
}

interface CopilotRecommendation {
  id: string;
  project_id: string;
  recommendation_type: string;
  title: string;
  description: string;
  action?: string;
  priority: number;
  created_at: string;
}

interface CopilotAction {
  id: string;
  project_id: string;
  action_type: string;
  title: string;
  description: string;
  metadata?: string;
  completed: string;
  created_at: string;
}

export const useCopilotChat = (projectId: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (request: CopilotChatRequest) => {
      const response = await client.post<CopilotChatResponse>(
        `/copilot/${projectId}/chat`,
        request
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["copilot", projectId, "history"],
      });
    },
  });
};

export const useCopilotHistory = (projectId: string, limit = 50) => {
  return useQuery({
    queryKey: ["copilot", projectId, "history"],
    queryFn: async () => {
      const response = await client.get<CopilotMessage[]>(
        `/copilot/${projectId}/history?limit=${limit}`
      );
      return response.data;
    },
  });
};

export const useCopilotMemory = (
  projectId: string,
  memoryType: string,
  key: string
) => {
  return useQuery({
    queryKey: ["copilot", projectId, "memory", memoryType, key],
    queryFn: async () => {
      const response = await client.get<CopilotMemory>(
        `/copilot/${projectId}/memory/${memoryType}/${key}`
      );
      return response.data;
    },
  });
};

export const useSaveCopilotMemory = (projectId: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (payload: {
      memory_type: string;
      key: string;
      value: Record<string, any>;
    }) => {
      const response = await client.post<CopilotMemory>(
        `/copilot/${projectId}/memory`,
        payload
      );
      return response.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({
        queryKey: ["copilot", projectId, "memory", data.memory_type, data.key],
      });
    },
  });
};

export const useCopilotRecommendations = (projectId: string, limit = 10) => {
  return useQuery({
    queryKey: ["copilot", projectId, "recommendations"],
    queryFn: async () => {
      const response = await client.get<CopilotRecommendation[]>(
        `/copilot/${projectId}/recommendations?limit=${limit}`
      );
      return response.data;
    },
  });
};

export const useCreateCopilotRecommendation = (projectId: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (payload: {
      recommendation_type: string;
      title: string;
      description: string;
      action?: string;
      priority?: number;
    }) => {
      const response = await client.post<CopilotRecommendation>(
        `/copilot/${projectId}/recommendations`,
        payload
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["copilot", projectId, "recommendations"],
      });
    },
  });
};

export const useCopilotActions = (projectId: string) => {
  return useQuery({
    queryKey: ["copilot", projectId, "actions"],
    queryFn: async () => {
      const response = await client.get<CopilotAction[]>(
        `/copilot/${projectId}/actions/pending`
      );
      return response.data;
    },
  });
};

export const useCreateCopilotAction = (projectId: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (payload: {
      action_type: string;
      title: string;
      description: string;
      metadata?: Record<string, any>;
    }) => {
      const response = await client.post<CopilotAction>(
        `/copilot/${projectId}/actions`,
        payload
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["copilot", projectId, "actions"],
      });
    },
  });
};

export const useCompleteCopilotAction = (projectId: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (actionId: string) => {
      const response = await client.post(
        `/copilot/${projectId}/actions/${actionId}/complete`
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["copilot", projectId, "actions"],
      });
    },
  });
};
