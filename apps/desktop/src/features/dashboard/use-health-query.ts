import { useQuery } from "@tanstack/react-query";

import { fetchHealth } from "@/lib/api/health";

export const useHealthQuery = () =>
  useQuery({
    queryKey: ["health"],
    queryFn: fetchHealth,
    retry: 1,
    refetchInterval: 30_000
  });
