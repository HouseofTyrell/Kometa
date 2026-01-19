<script setup lang="ts">
import { computed } from 'vue';
import { useUIStore, useConfigStore, useRunStore } from '@/stores';
import { useRunHistory, useValidateConfig, useCreateBackup, useSettings } from '@/api';
import { useToast } from '@/composables';
import { Card, Button, Badge, Spinner } from '@/components/common';
import type { TabId } from '@/types';

const ui = useUIStore();
const config = useConfigStore();
const runStore = useRunStore();
const toast = useToast();

// API hooks
const { data: history } = useRunHistory();
const { data: settings } = useSettings();
const validateMutation = useValidateConfig();
const createBackupMutation = useCreateBackup();

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

    <!-- System Status -->
    <Card>
      <template #header>
        <span class="font-medium">System Status</span>
      </template>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <!-- Apply Mode -->
        <div class="flex items-center gap-3 p-3 rounded-lg bg-surface-tertiary">
          <div class="w-10 h-10 rounded-full bg-surface-primary flex items-center justify-center">
            <svg class="w-5 h-5 text-content-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
            </svg>
          </div>
          <div class="flex-1 min-w-0">
            <div class="font-medium text-sm">Apply Mode</div>
            <Badge
              :variant="settings?.apply_enabled ? 'warning' : 'success'"
              size="sm"
            >
              {{ settings?.apply_enabled ? 'Enabled' : 'Safe Mode' }}
            </Badge>
          </div>
        </div>

        <!-- Version -->
        <div class="flex items-center gap-3 p-3 rounded-lg bg-surface-tertiary">
          <div class="w-10 h-10 rounded-full bg-surface-primary flex items-center justify-center">
            <svg class="w-5 h-5 text-content-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
          </div>
          <div class="flex-1 min-w-0">
            <div class="font-medium text-sm">Version</div>
            <Badge variant="default" size="sm">
              {{ settings?.version || '1.0.0' }}
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
