import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { client } from "./client";

interface Plugin {
  id: string;
  name: string;
  version: string;
  description: string;
  author: string;
  author_url?: string;
  license: string;
  repository_url?: string;
  documentation_url?: string;
  status: string;
  icon_url?: string;
  manifest: string;
  api_types: string;
  permissions: string;
  settings_schema?: string;
  sandbox_enabled: string;
  created_at: string;
  updated_at: string;
}

interface PluginInstallation {
  id: string;
  plugin_id: string;
  project_id: string;
  version_installed: string;
  status: string;
  auto_update: string;
  settings?: string;
  installed_at: string;
  enabled_at?: string;
  disabled_at?: string;
}

interface MarketplaceEntry {
  id: string;
  plugin_id: string;
  downloads: number;
  average_rating: number;
  total_ratings: number;
  featured: string;
  category?: string;
  tags?: string;
  changelog?: string;
  verified: string;
  verified_at?: string;
  published_at: string;
  updated_at: string;
}

export const useListPlugins = (
  status: string = "published",
  limit: number = 50
) => {
  return useQuery({
    queryKey: ["plugins", status],
    queryFn: async () => {
      const response = await client.get<Plugin[]>(
        `/plugins?status=${status}&limit=${limit}`
      );
      return response.data;
    },
  });
};

export const useGetPlugin = (pluginId: string) => {
  return useQuery({
    queryKey: ["plugins", pluginId],
    queryFn: async () => {
      const response = await client.get<Plugin>(`/plugins/${pluginId}`);
      return response.data;
    },
  });
};

export const useInstallPlugin = (projectId: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      pluginId,
      version,
      autoUpdate,
    }: {
      pluginId: string;
      version?: string;
      autoUpdate?: boolean;
    }) => {
      const response = await client.post<PluginInstallation>(
        `/plugins/${pluginId}/install?project_id=${projectId}`,
        {
          version,
          auto_update: autoUpdate !== undefined ? autoUpdate : true,
        }
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["plugins"] });
      queryClient.invalidateQueries({
        queryKey: ["plugin-installations", projectId],
      });
    },
  });
};

export const useUninstallPlugin = (projectId: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (pluginId: string) => {
      const response = await client.post<PluginInstallation>(
        `/plugins/${pluginId}/uninstall?project_id=${projectId}`
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["plugin-installations", projectId],
      });
    },
  });
};

export const useEnablePlugin = (projectId: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (pluginId: string) => {
      const response = await client.post<PluginInstallation>(
        `/plugins/${pluginId}/enable?project_id=${projectId}`
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["plugin-installations", projectId],
      });
    },
  });
};

export const useDisablePlugin = (projectId: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (pluginId: string) => {
      const response = await client.post<PluginInstallation>(
        `/plugins/${pluginId}/disable?project_id=${projectId}`
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["plugin-installations", projectId],
      });
    },
  });
};

export const useGetPluginInstallations = (projectId: string) => {
  return useQuery({
    queryKey: ["plugin-installations", projectId],
    queryFn: async () => {
      const response = await client.get<PluginInstallation[]>(
        `/plugins/installations?project_id=${projectId}`
      );
      return response.data;
    },
  });
};

export const useGetMarketplace = (category?: string, limit: number = 50) => {
  return useQuery({
    queryKey: ["marketplace", category],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (category) params.append("category", category);
      params.append("limit", limit.toString());

      const response = await client.get<MarketplaceEntry[]>(
        `/marketplace?${params}`
      );
      return response.data;
    },
  });
};

export const useRatePlugin = (projectId: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      pluginId,
      rating,
      title,
      review,
    }: {
      pluginId: string;
      rating: number;
      title?: string;
      review?: string;
    }) => {
      const response = await client.post(
        `/plugins/${pluginId}/rate?project_id=${projectId}`,
        { rating, title, review }
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["marketplace"] });
    },
  });
};

export const useUpdatePluginSettings = (projectId: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      pluginId,
      settings,
    }: {
      pluginId: string;
      settings: Record<string, any>;
    }) => {
      const response = await client.put(
        `/plugins/${pluginId}/settings?project_id=${projectId}`,
        { settings }
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["plugin-installations", projectId],
      });
    },
  });
};

export const useConnectOAuth = (projectId: string) => {
  return useMutation({
    mutationFn: async ({
      pluginId,
      provider,
      code,
      redirectUri,
    }: {
      pluginId: string;
      provider: string;
      code: string;
      redirectUri: string;
    }) => {
      const response = await client.post(
        `/plugins/${pluginId}/oauth?project_id=${projectId}`,
        { provider, code, redirect_uri: redirectUri }
      );
      return response.data;
    },
  });
};
