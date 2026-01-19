<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { Card, Button, Badge, Input, Select, Checkbox } from '@/components/common';
import FormField from './FormField.vue';
import { useSchedulerStatus, useConfigureScheduler, useStopScheduler } from '@/api';
import { useToast } from '@/composables';

const toast = useToast();

// API hooks
const { data: status, isLoading, refetch } = useSchedulerStatus();
const configureMutation = useConfigureScheduler();
const stopMutation = useStopScheduler();

// Local state for form
const enabled = ref(false);
const scheduleExpression = ref('daily');
const dryRunOnly = ref(true);

// Sync local state with API data
watch(status, (newStatus) => {
  if (newStatus) {
    enabled.value = newStatus.enabled;
    scheduleExpression.value = newStatus.schedule || 'daily';
    dryRunOnly.value = newStatus.dry_run_only;
  }
}, { immediate: true });

// Schedule presets
const schedulePresets = [
  { value: 'hourly', label: 'Hourly' },
  { value: 'daily', label: 'Daily (midnight)' },
  { value: 'weekly(sunday)', label: 'Weekly (Sunday)' },
  { value: 'weekly(monday)', label: 'Weekly (Monday)' },
  { value: 'weekly(friday)', label: 'Weekly (Friday)' },
  { value: 'monthly(1)', label: 'Monthly (1st)' },
  { value: 'monthly(15)', label: 'Monthly (15th)' },
];

// Computed
const isConfiguring = computed(() => configureMutation.isPending.value || stopMutation.isPending.value);

const nextRunFormatted = computed(() => {
  if (!status.value?.next_run) return null;
  const date = new Date(status.value.next_run);
  return date.toLocaleString();
});

const lastRunFormatted = computed(() => {
  if (!status.value?.last_run) return null;
  const date = new Date(status.value.last_run);
  return date.toLocaleString();
});

const timeUntilNextRun = computed(() => {
  if (!status.value?.next_run) return null;
  const now = new Date();
  const next = new Date(status.value.next_run);
  const diff = next.getTime() - now.getTime();

  if (diff <= 0) return 'Imminent';

  const hours = Math.floor(diff / (1000 * 60 * 60));
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));

  if (hours > 24) {
    const days = Math.floor(hours / 24);
    return `${days} day${days > 1 ? 's' : ''}`;
  }
  if (hours > 0) {
    return `${hours}h ${minutes}m`;
  }
  return `${minutes} minutes`;
});

// Actions
async function saveScheduler() {
  try {
    await configureMutation.mutateAsync({
      enabled: enabled.value,
      schedule: scheduleExpression.value,
      dry_run_only: dryRunOnly.value,
    });
    toast.success(enabled.value ? 'Scheduler enabled' : 'Scheduler disabled');
  } catch (err) {
    toast.error('Failed to configure scheduler');
  }
}

async function stopScheduler() {
  try {
    await stopMutation.mutateAsync();
    enabled.value = false;
    toast.success('Scheduler stopped');
  } catch (err) {
    toast.error('Failed to stop scheduler');
  }
}
</script>

<template>
  <Card class="relative overflow-hidden">
    <!-- Status indicator bar -->
    <div
      class="absolute top-0 left-0 right-0 h-1"
      :class="status?.enabled ? 'bg-success' : 'bg-content-muted'"
    />

    <div class="p-5">
      <!-- Header -->
      <div class="flex items-start justify-between mb-6">
        <div class="flex items-center gap-3">
          <div
            class="w-10 h-10 rounded-lg flex items-center justify-center text-xl"
            :class="status?.enabled ? 'bg-success/10' : 'bg-surface-tertiary'"
          >
            {{ status?.enabled ? '⏰' : '🕐' }}
          </div>
          <div>
            <h3 class="font-semibold flex items-center gap-2">
              Automated Scheduler
              <Badge :variant="status?.enabled ? 'success' : 'default'" size="sm">
                {{ status?.enabled ? 'Running' : 'Stopped' }}
              </Badge>
            </h3>
            <p class="text-sm text-content-secondary">
              Automatically run Kometa on a schedule
            </p>
          </div>
        </div>

        <div v-if="status?.enabled" class="text-right">
          <p class="text-xs text-content-muted">Next run</p>
          <p class="font-medium text-kometa-gold">{{ timeUntilNextRun }}</p>
        </div>
      </div>

      <!-- Status Details (when enabled) -->
      <div v-if="status?.enabled" class="mb-6 p-4 rounded-lg bg-success/5 border border-success/20">
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <p class="text-content-muted">Schedule</p>
            <p class="font-medium">{{ status.schedule }}</p>
          </div>
          <div>
            <p class="text-content-muted">Next Run</p>
            <p class="font-medium">{{ nextRunFormatted || 'Calculating...' }}</p>
          </div>
          <div>
            <p class="text-content-muted">Last Run</p>
            <p class="font-medium">{{ lastRunFormatted || 'Never' }}</p>
          </div>
          <div>
            <p class="text-content-muted">Total Runs</p>
            <p class="font-medium">{{ status.run_count }}</p>
          </div>
        </div>

        <div class="mt-3 flex items-center gap-2 text-sm">
          <Badge :variant="status.dry_run_only ? 'warning' : 'error'" size="sm">
            {{ status.dry_run_only ? 'Dry Run Only' : 'Apply Mode' }}
          </Badge>
          <span class="text-content-secondary">
            {{ status.dry_run_only
              ? 'Changes will be previewed but not applied'
              : 'Changes will be applied to your libraries' }}
          </span>
        </div>
      </div>

      <!-- Configuration Form -->
      <div class="space-y-4">
        <div class="flex items-center gap-3">
          <Checkbox
            v-model="enabled"
            :disabled="isConfiguring"
          >
            Enable automated scheduling
          </Checkbox>
        </div>

        <div v-if="enabled" class="pl-7 space-y-4 border-l-2 border-kometa-gold/30">
          <FormField
            label="Schedule"
            tooltip="When Kometa should automatically run"
          >
            <Select
              v-model="scheduleExpression"
              :options="schedulePresets"
              :disabled="isConfiguring"
            />
          </FormField>

          <FormField
            label="Run Mode"
            tooltip="Whether to apply changes or just preview them"
          >
            <div class="flex gap-4">
              <label class="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  v-model="dryRunOnly"
                  :value="true"
                  :disabled="isConfiguring"
                  class="text-kometa-gold focus:ring-kometa-gold"
                />
                <span>Dry Run Only</span>
                <span class="text-xs text-content-muted">(Safe)</span>
              </label>
              <label class="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  v-model="dryRunOnly"
                  :value="false"
                  :disabled="isConfiguring"
                  class="text-kometa-gold focus:ring-kometa-gold"
                />
                <span>Apply Changes</span>
                <span class="text-xs text-error">(Modifies Library)</span>
              </label>
            </div>
          </FormField>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex items-center gap-3 mt-6 pt-4 border-t border-border">
        <Button
          :variant="enabled ? 'primary' : 'secondary'"
          :disabled="isConfiguring"
          @click="saveScheduler"
        >
          <svg v-if="isConfiguring" class="w-4 h-4 mr-2 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          {{ enabled ? 'Start Scheduler' : 'Save Settings' }}
        </Button>

        <Button
          v-if="status?.enabled"
          variant="ghost"
          :disabled="isConfiguring"
          @click="stopScheduler"
        >
          Stop Scheduler
        </Button>

        <Button
          variant="ghost"
          @click="refetch()"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </Button>
      </div>

      <!-- Help text -->
      <p class="mt-4 text-xs text-content-muted">
        The scheduler runs within the Web UI process. Keep the Web UI running for scheduled runs to work.
        For production deployments, consider using an external scheduler like cron.
      </p>
    </div>
  </Card>
</template>
