import { useQuery, useMutation } from "@tanstack/react-query";
import { client } from "./client";

export interface EditOperation {
  id: string;
  edit_plan_id: string;
  clip_id?: string;
  operation_type: string;
  start_time: number;
  end_time: number;
  title: string;
  description?: string;
  reason?: string;
  suggestion_id?: string;
  enabled: boolean;
  applied: boolean;
  order: number;
  created_at: string;
}

export interface TimelineClip {
  id: string;
  track_id: string;
  start_time: number;
  end_time: number;
  source_start?: number;
  source_end?: number;
  clip_type: string;
  title?: string;
  description?: string;
  enabled: boolean;
  created_at: string;
}

export interface TimelineTrack {
  id: string;
  edit_plan_id: string;
  track_type: string;
  order: number;
  height: number;
  locked: boolean;
  visible: boolean;
  label?: string;
  clips: TimelineClip[];
  created_at: string;
}

export interface EditPlan {
  id: string;
  project_id: string;
  version: number;
  status: string;
  approved: boolean;
  estimated_duration?: number;
  estimated_render_time?: number;
  change_count: number;
  tracks: TimelineTrack[];
  operations: EditOperation[];
  created_at: string;
  updated_at: string;
}

// Fetch edit plan for project
export const useEditPlan = (projectId: string) => {
  return useQuery({
    queryKey: ["edit-plan", projectId],
    queryFn: async () => {
      const response = await client.get<EditPlan>(
        `/projects/${projectId}/edit-plan`
      );
      return response.data;
    },
    enabled: !!projectId,
  });
};

// Generate edit plan
export const useGenerateEditPlan = () => {
  return useMutation({
    mutationFn: async (projectId: string) => {
      const response = await client.post<EditPlan>(
        `/projects/${projectId}/edit-plan`
      );
      return response.data;
    },
  });
};

// Approve edit plan
export const useApproveEditPlan = () => {
  return useMutation({
    mutationFn: async (planId: string) => {
      const response = await client.post<EditPlan>(
        `/edit-plan/${planId}/approve`,
        { approved: true }
      );
      return response.data;
    },
  });
};

// Regenerate edit plan
export const useRegenerateEditPlan = () => {
  return useMutation({
    mutationFn: async ({
      planId,
      prompt,
    }: {
      planId: string;
      prompt: string;
    }) => {
      const response = await client.post<EditPlan>(
        `/edit-plan/${planId}/regenerate`,
        { prompt }
      );
      return response.data;
    },
  });
};

// Undo edit plan
export const useUndoEditPlan = () => {
  return useMutation({
    mutationFn: async (planId: string) => {
      const response = await client.post<EditPlan>(`/edit-plan/${planId}/undo`);
      return response.data;
    },
  });
};

// Redo edit plan
export const useRedoEditPlan = () => {
  return useMutation({
    mutationFn: async (planId: string) => {
      const response = await client.post<EditPlan>(`/edit-plan/${planId}/redo`);
      return response.data;
    },
  });
};
