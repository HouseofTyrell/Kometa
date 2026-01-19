/**
 * Scheduler API hooks
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query';
import { api } from './client';

// Query keys
export const schedulerKeys = {
  all: ['scheduler'] as const,
  status: () => [...schedulerKeys.all, 'status'] as const,
};

// Types
export interface SchedulerStatus {
  enabled: boolean;
  schedule: string | null;
  dry_run_only: boolean;
  next_run: string | null;
  last_run: string | null;
  run_count: number;
}

interface SchedulerConfigParams {
  enabled: boolean;
  schedule?: string;
  dry_run_only?: boolean;
}

interface SchedulerConfigResponse {
  success: boolean;
  message: string;
  status: SchedulerStatus;
}

/**
 * Get scheduler status
 */
export function useSchedulerStatus() {
  return useQuery({
    queryKey: schedulerKeys.status(),
    queryFn: async () => {
      const response = await api.get<SchedulerStatus>('/scheduler/status');
      return response;
    },
    refetchInterval: 30000, // Refresh every 30 seconds
  });
}

/**
 * Configure scheduler
 */
export function useConfigureScheduler() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (params: SchedulerConfigParams) => {
      const response = await api.post<SchedulerConfigResponse>('/scheduler/configure', params);
      return response;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: schedulerKeys.status() });
    },
  });
}

/**
 * Stop scheduler
 */
export function useStopScheduler() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async () => {
      const response = await api.post<SchedulerConfigResponse>('/scheduler/stop', {});
      return response;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: schedulerKeys.status() });
    },
  });
}
