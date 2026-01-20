import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { TestableService } from '@/api';

export interface ConnectionStatus {
  service: TestableService;
  tested: boolean;
  success: boolean;
  message?: string;
  testedAt?: Date;
}

export const useConnectionsStore = defineStore('connections', () => {
  // State - tracks the connection status for each service
  const statuses = ref<Map<TestableService, ConnectionStatus>>(new Map());

  // Getters
  const getStatus = computed(() => (service: TestableService) => {
    return statuses.value.get(service);
  });

  const isConnected = computed(() => (service: TestableService) => {
    const status = statuses.value.get(service);
    return status?.tested && status?.success;
  });

  const hasTested = computed(() => (service: TestableService) => {
    const status = statuses.value.get(service);
    return status?.tested ?? false;
  });

  // Actions
  function setConnectionStatus(
    service: TestableService,
    success: boolean,
    message?: string
  ) {
    statuses.value.set(service, {
      service,
      tested: true,
      success,
      message,
      testedAt: new Date(),
    });
  }

  function clearStatus(service: TestableService) {
    statuses.value.delete(service);
  }

  function clearAllStatuses() {
    statuses.value.clear();
  }

  return {
    // State
    statuses,

    // Getters
    getStatus,
    isConnected,
    hasTested,

    // Actions
    setConnectionStatus,
    clearStatus,
    clearAllStatuses,
  };
});
