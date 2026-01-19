<script setup lang="ts">
import { computed } from 'vue';
import { useUIStore, useConfigStore, useRunStore } from '@/stores';
import { useTestAllConnections, useRunHistory, useValidateConfig, useCreateBackup } from '@/api';
import { useToast } from '@/composables';
import { Card, Button, Badge, Spinner } from '@/components/common';
import type { TabId } from '@/types';

const ui = useUIStore();
const config = useConfigStore();
const runStore = useRunStore();
const toast = useToast();

// API hooks
const { data: history } = useRunHistory();
const validateMutation = useValidateConfig();
const createBackupMutation = useCreateBackup();
const testConnectionsMutation = useTestAllConnections();

// Connection status
const connectionStatus = computed(() => testConnectionsMutation.data.value);
const isTestingConnections = computed(() => testConnectionsMutation.isPending.value);

// Recent activity from run history
const recentRuns = computed(() => {
  if (!history.value) return [];
  return history.value.slice(0, 5);
});

// Quick actions
const quickActions = [
  {
    id: 'upload',
    label: 'Upload Config',
    description: 'Import a config.yml file',
    icon: 'M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12',
    action: () => navigateTo('config'),
  },
  {
    id: 'run',
    label: 'Run Kometa',
    description: 'Execute with current config',
    icon: 'M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z',
    action: () => navigateTo('run'),
  },
  {
    id: 'validate',
    label: 'Validate Config',
    description: 'Check configuration for errors',
    icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z',
    action: handleValidate,
  },
  {
    id: 'backup',
    label: 'Backup Config',
    description: 'Save a backup of current config',
    icon: 'M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4',
    action: handleBackup,
  },
];

// Navigate to a tab
function navigateTo(tab: TabId) {
  ui.setActiveTab(tab);
}

// Validate config
async function handleValidate() {
  if (!config.rawConfig) {
    toast.warning('No configuration loaded');
    return;
  }

  try {
    const result = await validateMutation.mutateAsync(config.rawConfig);
    config.setValidation(result);
    if (result.errors.length === 0) {
      toast.success('Configuration is valid');
    } else {
      toast.error(`Found ${result.errors.length} error(s)`);
    }
  } catch (err) {
    toast.error('Validation failed');
  }
}

// Create backup
async function handleBackup() {
  try {
    const result = await createBackupMutation.mutateAsync();
    toast.success(`Backup created: ${result.filename}`);
  } catch (err) {
    toast.error('Failed to create backup');
  }
}

// Test connections
async function handleTestConnections() {
  try {
    await testConnectionsMutation.mutateAsync();
    toast.success('Connection tests complete');
  } catch (err) {
    toast.error('Connection tests failed');
  }
}

// Format date
function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleString();
}

// Format duration
function formatDuration(seconds: number) {
  if (seconds < 60) return `${seconds}s`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${seconds % 60}s`;
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  return `${h}h ${m}m`;
}

// Get status color
function getStatusVariant(status: string): 'success' | 'error' | 'warning' | 'default' {
  switch (status) {
    case 'completed':
    case 'connected':
      return 'success';
    case 'failed':
    case 'error':
      return 'error';
    case 'running':
    case 'pending':
      return 'warning';
    default:
      return 'default';
  }
}
</script>

<template>
  <div class="h-full overflow-auto p-4 space-y-6">
    <!-- Header -->
    <div>
      <h2 class="text-xl font-semibold text-content-primary">
        Dashboard
      </h2>
      <p class="text-sm text-content-secondary mt-0.5">
        System status and quick actions
      </p>
    </div>

    <!-- Quick Actions -->
    <Card>
      <template #header>
        <span class="font-medium">Quick Actions</span>
      </template>

      <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
        <button
          v-for="action in quickActions"
          :key="action.id"
          class="flex flex-col items-center gap-2 p-4 rounded-lg bg-surface-tertiary
                 hover:bg-surface-hover transition-colors text-center group"
          @click="action.action"
        >
          <div class="w-10 h-10 rounded-full bg-kometa-gold/10 flex items-center justify-center
                      group-hover:bg-kometa-gold/20 transition-colors">
            <svg
              class="w-5 h-5 text-kometa-gold"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                :d="action.icon"
              />
            </svg>
          </div>
          <div>
            <div class="font-medium text-sm text-content">
              {{ action.label }}
            </div>
            <div class="text-xs text-content-muted mt-0.5">
              {{ action.description }}
            </div>
          </div>
        </button>
      </div>
    </Card>

    <!-- Connection Status -->
    <Card>
      <template #header>
        <div class="flex items-center justify-between w-full">
          <span class="font-medium">Connection Status</span>
          <Button
            variant="secondary"
            size="sm"
            :loading="isTestingConnections"
            @click="handleTestConnections"
          >
            Test All
          </Button>
        </div>
      </template>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <!-- Plex -->
        <div class="flex items-center gap-3 p-3 rounded-lg bg-surface-tertiary">
          <div class="w-10 h-10 rounded-full bg-surface-primary flex items-center justify-center">
            <svg class="w-5 h-5 text-content-secondary" fill="currentColor" viewBox="0 0 24 24">
              <path d="M5.414 3.846L18.586 3.846C20.484 3.846 22 5.362 22 7.26L22 16.74C22 18.638 20.484 20.154 18.586 20.154L5.414 20.154C3.516 20.154 2 18.638 2 16.74L2 7.26C2 5.362 3.516 3.846 5.414 3.846ZM7.5 7.5L12 12L7.5 16.5L7.5 7.5Z"/>
            </svg>
          </div>
          <div class="flex-1 min-w-0">
            <div class="font-medium text-sm">Plex Server</div>
            <Badge
              :variant="connectionStatus?.plex?.connected ? 'success' : 'default'"
              size="sm"
            >
              {{ connectionStatus?.plex?.connected ? 'Connected' : 'Not configured' }}
            </Badge>
          </div>
        </div>

        <!-- TMDb -->
        <div class="flex items-center gap-3 p-3 rounded-lg bg-surface-tertiary">
          <div class="w-10 h-10 rounded-full bg-surface-primary flex items-center justify-center">
            <svg class="w-5 h-5 text-content-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z"/>
            </svg>
          </div>
          <div class="flex-1 min-w-0">
            <div class="font-medium text-sm">TMDb API</div>
            <Badge
              :variant="connectionStatus?.tmdb?.connected ? 'success' : 'default'"
              size="sm"
            >
              {{ connectionStatus?.tmdb?.connected ? 'Connected' : 'Not configured' }}
            </Badge>
          </div>
        </div>

        <!-- Config -->
        <div class="flex items-center gap-3 p-3 rounded-lg bg-surface-tertiary">
          <div class="w-10 h-10 rounded-full bg-surface-primary flex items-center justify-center">
            <svg class="w-5 h-5 text-content-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
            </svg>
          </div>
          <div class="flex-1 min-w-0">
            <div class="font-medium text-sm">Configuration</div>
            <Badge
              :variant="config.isValid ? 'success' : config.hasErrors ? 'error' : 'default'"
              size="sm"
            >
              {{ config.isValid ? 'Valid' : config.hasErrors ? 'Has errors' : 'Not loaded' }}
            </Badge>
          </div>
          <Button
            variant="ghost"
            size="sm"
            @click="navigateTo('config')"
          >
            Edit
          </Button>
        </div>
      </div>
    </Card>

    <!-- Run Status (if running) -->
    <Card v-if="runStore.isRunning">
      <template #header>
        <div class="flex items-center gap-2">
          <Spinner size="sm" />
          <span class="font-medium">Run in Progress</span>
        </div>
      </template>

      <div class="space-y-3">
        <div class="flex items-center justify-between">
          <span class="text-sm text-content-secondary">Current Library</span>
          <span class="text-sm font-medium">{{ runStore.currentRun?.current_library || '-' }}</span>
        </div>
        <div class="flex items-center justify-between">
          <span class="text-sm text-content-secondary">Status</span>
          <Badge variant="warning">{{ runStore.currentRun?.status || 'Running' }}</Badge>
        </div>
        <Button
          variant="secondary"
          class="w-full"
          @click="navigateTo('logs')"
        >
          View Logs
        </Button>
      </div>
    </Card>

    <!-- Recent Activity -->
    <Card>
      <template #header>
        <div class="flex items-center justify-between w-full">
          <span class="font-medium">Recent Activity</span>
          <Button
            v-if="recentRuns.length > 0"
            variant="ghost"
            size="sm"
            @click="navigateTo('history')"
          >
            View All
          </Button>
        </div>
      </template>

      <div v-if="recentRuns.length > 0" class="space-y-2">
        <div
          v-for="run in recentRuns"
          :key="run.id"
          class="flex items-center justify-between p-3 rounded-lg bg-surface-tertiary"
        >
          <div class="flex items-center gap-3">
            <Badge :variant="getStatusVariant(run.status)">
              {{ run.status }}
            </Badge>
            <div>
              <div class="text-sm font-medium">
                {{ run.type === 'dry_run' ? 'Dry Run' : 'Full Run' }}
              </div>
              <div class="text-xs text-content-muted">
                {{ formatDate(run.started_at) }}
              </div>
            </div>
          </div>
          <div class="text-sm text-content-secondary">
            {{ run.duration ? formatDuration(run.duration) : '-' }}
          </div>
        </div>
      </div>

      <div v-else class="text-center py-8 text-content-muted">
        <svg class="w-12 h-12 mx-auto mb-2 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
        </svg>
        <p>No recent activity</p>
        <Button
          variant="secondary"
          size="sm"
          class="mt-3"
          @click="navigateTo('run')"
        >
          Start a Run
        </Button>
      </div>
    </Card>
  </div>
</template>
