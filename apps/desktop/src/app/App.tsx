import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import { createQueryClient } from "@/app/query-client";
import { DashboardShell } from "@/components/layout/dashboard-shell";

const queryClient: QueryClient = createQueryClient();

export const App = (): JSX.Element => {
  return (
    <QueryClientProvider client={queryClient}>
      <DashboardShell />
    </QueryClientProvider>
  );
};
