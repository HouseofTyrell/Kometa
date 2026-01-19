<script setup lang="ts">
import { computed } from 'vue';
import FormField from '../FormField.vue';
import { Input, Checkbox } from '@/components/common';

interface TautulliConfig {
  url?: string;
  apikey?: string;
}

interface Props {
  modelValue: TautulliConfig;
}

const props = defineProps<Props>();
const emit = defineEmits<{
  (e: 'update:modelValue', value: TautulliConfig): void;
  (e: 'test-connection'): void;
}>();

function updateField<K extends keyof TautulliConfig>(field: K, value: TautulliConfig[K]) {
  emit('update:modelValue', { ...props.modelValue, [field]: value });
}

const isConfigured = computed(() => !!props.modelValue.url && !!props.modelValue.apikey);
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-start justify-between">
      <div>
        <div class="flex items-center gap-2">
          <span class="text-2xl">📊</span>
          <h3 class="text-lg font-semibold">Tautulli Configuration</h3>
          <span class="text-xs px-2 py-0.5 rounded bg-surface-tertiary text-content-muted font-medium">Optional</span>
        </div>
        <p class="mt-1 text-sm text-content-secondary">
          Connect Tautulli for watch history and popularity-based collection builders.
        </p>
      </div>
      <a
        href="https://kometa.wiki/en/latest/config/tautulli/"
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

    <!-- Connection Status -->
    <div
      class="p-4 rounded-lg"
      :class="isConfigured ? 'bg-success/10 border border-success/20' : 'bg-surface-tertiary'"
    >
      <div class="flex items-center gap-3">
        <span :class="isConfigured ? 'text-success' : 'text-content-muted'" class="text-xl">
          {{ isConfigured ? '✓' : '📊' }}
        </span>
        <div class="flex-1">
          <p class="font-medium" :class="isConfigured ? 'text-success' : 'text-content'">
            {{ isConfigured ? 'Tautulli Connected' : 'Connect Tautulli' }}
          </p>
          <p class="text-sm text-content-secondary">
            {{ isConfigured
              ? 'Your Tautulli instance is configured.'
              : 'Enter your Tautulli URL and API key to enable watch history features.' }}
          </p>
        </div>
      </div>
    </div>

    <!-- Connection Settings -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <FormField
        label="Tautulli URL"
        required
        tooltip="The URL to your Tautulli instance"
        help="e.g., http://localhost:8181"
      >
        <Input
          :model-value="props.modelValue.url || ''"
          placeholder="http://localhost:8181"
          @update:model-value="updateField('url', $event)"
        />
      </FormField>

      <FormField
        label="API Key"
        required
        tooltip="Your Tautulli API key (Settings > Web Interface > API Key)"
      >
        <Input
          type="password"
          :model-value="props.modelValue.apikey || ''"
          placeholder="Your Tautulli API key"
          @update:model-value="updateField('apikey', $event)"
        />
      </FormField>
    </div>

    <!-- Test Connection -->
    <div class="flex items-center gap-4 p-4 rounded-lg bg-surface-tertiary">
      <button
        class="px-4 py-2 rounded-lg bg-kometa-gold text-black font-medium hover:bg-kometa-gold/90 transition-colors"
        @click="emit('test-connection')"
      >
        Test Connection
      </button>
      <span class="text-sm text-content-secondary">
        Verify your Tautulli instance is accessible
      </span>
    </div>

    <!-- Usage Examples -->
    <div class="border-t border-border pt-6">
      <h4 class="font-medium mb-4 flex items-center gap-2">
        <span>📚</span> Tautulli Builders
      </h4>
      <p class="text-sm text-content-secondary mb-4">
        Once connected, you can use these Tautulli builders in your collection files:
      </p>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
        <div class="p-3 rounded bg-surface-tertiary">
          <code class="text-kometa-gold">tautulli_popular</code>
          <p class="text-content-secondary mt-1">Most watched items by all users</p>
        </div>
        <div class="p-3 rounded bg-surface-tertiary">
          <code class="text-kometa-gold">tautulli_watched</code>
          <p class="text-content-secondary mt-1">Items watched by specific users</p>
        </div>
      </div>
    </div>

    <!-- How It Works -->
    <div class="border-t border-border pt-6">
      <h4 class="font-medium mb-4 flex items-center gap-2">
        <span>💡</span> How It Works
      </h4>
      <div class="p-4 rounded-lg bg-surface-tertiary text-sm">
        <p class="text-content-secondary mb-3">
          Tautulli tracks detailed Plex watch history and statistics. When connected to Kometa:
        </p>
        <ul class="list-disc list-inside space-y-1 text-content-secondary">
          <li>Build collections based on most-watched content</li>
          <li>Create personalized "Most Popular" collections</li>
          <li>Filter by time period (last 7 days, 30 days, etc.)</li>
          <li>Track watch counts and play duration</li>
        </ul>
      </div>
    </div>
  </div>
</template>
