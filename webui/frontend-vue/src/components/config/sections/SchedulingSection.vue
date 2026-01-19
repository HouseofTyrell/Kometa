<script setup lang="ts">
import { ref, computed } from 'vue';
import FormField from '../FormField.vue';
import { Input, Select, Checkbox, Button, Card } from '@/components/common';

interface ScheduleConfig {
  run_order?: string[];
  schedule?: string;
}

interface Props {
  modelValue: ScheduleConfig;
  libraries?: Record<string, { schedule?: string }>;
}

const props = defineProps<Props>();
const emit = defineEmits<{
  (e: 'update:modelValue', value: ScheduleConfig): void;
  (e: 'update:libraries', value: Record<string, { schedule?: string }>): void;
}>();

function updateField<K extends keyof ScheduleConfig>(field: K, value: ScheduleConfig[K]) {
  emit('update:modelValue', { ...props.modelValue, [field]: value });
}

// Run order management
const runOrderOptions = [
  { id: 'operations', label: 'Operations', icon: '⚡' },
  { id: 'metadata', label: 'Metadata', icon: '🏷️' },
  { id: 'collections', label: 'Collections', icon: '📚' },
  { id: 'overlays', label: 'Overlays', icon: '🎨' },
];

const currentRunOrder = computed(() =>
  props.modelValue.run_order || ['operations', 'metadata', 'collections', 'overlays']
);

function moveRunOrderItem(index: number, direction: 'up' | 'down') {
  const newOrder = [...currentRunOrder.value];
  const newIndex = direction === 'up' ? index - 1 : index + 1;
  if (newIndex < 0 || newIndex >= newOrder.length) return;

  [newOrder[index], newOrder[newIndex]] = [newOrder[newIndex], newOrder[index]];
  updateField('run_order', newOrder);
}

// Schedule presets
const schedulePresets = [
  { value: '', label: 'Custom' },
  { value: 'hourly', label: 'Hourly' },
  { value: 'daily', label: 'Daily (at midnight)' },
  { value: 'weekly(sunday)', label: 'Weekly (Sunday)' },
  { value: 'weekly(monday)', label: 'Weekly (Monday)' },
  { value: 'monthly(1)', label: 'Monthly (1st)' },
  { value: 'monthly(15)', label: 'Monthly (15th)' },
];

const selectedPreset = ref('');
const customSchedule = ref(props.modelValue.schedule || '');

function applyPreset(preset: string) {
  if (preset) {
    customSchedule.value = preset;
    updateField('schedule', preset);
  }
}

// Schedule syntax examples
const scheduleExamples = [
  { syntax: 'hourly', description: 'Run every hour' },
  { syntax: 'daily', description: 'Run daily at midnight' },
  { syntax: 'weekly(sunday)', description: 'Run every Sunday' },
  { syntax: 'monthly(1)', description: 'Run on the 1st of each month' },
  { syntax: 'range(05:00-08:00)', description: 'Run only between 5am-8am' },
  { syntax: 'all[weekly(friday), range(18:00-22:00)]', description: 'Friday evenings only' },
];
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-start justify-between">
      <div>
        <div class="flex items-center gap-2">
          <span class="text-2xl">🕐</span>
          <h3 class="text-lg font-semibold">Scheduling</h3>
          <span class="text-xs px-2 py-0.5 rounded bg-surface-tertiary text-content-muted font-medium">Optional</span>
        </div>
        <p class="mt-1 text-sm text-content-secondary">
          Configure when and how Kometa runs, including run order and scheduling.
        </p>
      </div>
      <a
        href="https://kometa.wiki/en/latest/config/schedule/"
        target="_blank"
        class="flex items-center gap-1 text-sm text-kometa-gold hover:underline"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
        </svg>
        Documentation
      </a>
    </div>

    <!-- Run Order -->
    <div class="border-t border-border pt-6">
      <h4 class="font-medium mb-4 flex items-center gap-2">
        <span>📋</span> Run Order
      </h4>
      <p class="text-sm text-content-secondary mb-4">
        Drag to reorder or use arrows to change the order in which Kometa processes items.
      </p>

      <div class="space-y-2">
        <div
          v-for="(item, index) in currentRunOrder"
          :key="item"
          class="flex items-center gap-3 p-3 rounded-lg bg-surface-tertiary"
        >
          <span class="text-lg text-content-muted">{{ index + 1 }}</span>
          <span class="text-xl">{{ runOrderOptions.find(o => o.id === item)?.icon }}</span>
          <span class="flex-1 font-medium">{{ runOrderOptions.find(o => o.id === item)?.label }}</span>
          <div class="flex gap-1">
            <button
              class="p-1.5 rounded hover:bg-surface-hover disabled:opacity-50"
              :disabled="index === 0"
              @click="moveRunOrderItem(index, 'up')"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
              </svg>
            </button>
            <button
              class="p-1.5 rounded hover:bg-surface-hover disabled:opacity-50"
              :disabled="index === currentRunOrder.length - 1"
              @click="moveRunOrderItem(index, 'down')"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Global Schedule -->
    <div class="border-t border-border pt-6">
      <h4 class="font-medium mb-4 flex items-center gap-2">
        <span>⏰</span> Global Schedule
      </h4>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <FormField
          label="Schedule Preset"
          help="Quick presets for common schedules"
        >
          <Select
            v-model="selectedPreset"
            :options="schedulePresets"
            @update:model-value="applyPreset($event)"
          />
        </FormField>

        <FormField
          label="Schedule Expression"
          tooltip="Custom schedule using Kometa schedule syntax"
          help="e.g., daily, weekly(sunday), range(05:00-08:00)"
        >
          <Input
            v-model="customSchedule"
            placeholder="daily"
            @update:model-value="updateField('schedule', $event)"
          />
        </FormField>
      </div>

      <!-- Schedule Syntax Help -->
      <Card class="bg-surface-tertiary">
        <h5 class="text-sm font-medium mb-3">Schedule Syntax Examples</h5>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
          <div
            v-for="example in scheduleExamples"
            :key="example.syntax"
            class="flex items-start gap-2"
          >
            <code class="px-1.5 py-0.5 rounded bg-surface-primary font-mono text-xs">{{ example.syntax }}</code>
            <span class="text-content-secondary">{{ example.description }}</span>
          </div>
        </div>
      </Card>
    </div>

    <!-- Library-Specific Schedules -->
    <div v-if="props.libraries && Object.keys(props.libraries).length > 0" class="border-t border-border pt-6">
      <h4 class="font-medium mb-4 flex items-center gap-2">
        <span>📚</span> Library Schedules
      </h4>
      <p class="text-sm text-content-secondary mb-4">
        Override the global schedule for specific libraries.
      </p>

      <div class="space-y-3">
        <div
          v-for="(config, libName) in props.libraries"
          :key="libName"
          class="flex items-center gap-4 p-3 rounded-lg bg-surface-tertiary"
        >
          <span class="font-medium min-w-[150px]">{{ libName }}</span>
          <Input
            :model-value="config.schedule || ''"
            placeholder="Use global schedule"
            class="flex-1"
            @update:model-value="emit('update:libraries', {
              ...props.libraries,
              [libName]: { ...config, schedule: $event }
            })"
          />
        </div>
      </div>
    </div>
  </div>
</template>
