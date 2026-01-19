<script setup lang="ts">
import { computed } from 'vue';
import FormField from '../FormField.vue';
import { Input, Checkbox, Select } from '@/components/common';

interface NotifiarrConfig {
  apikey?: string;
  run_start_notify?: boolean;
  run_end_notify?: boolean;
  sync_notify?: boolean;
  error_notify?: boolean;
}

interface Props {
  modelValue: NotifiarrConfig;
}

const props = defineProps<Props>();
const emit = defineEmits<{
  (e: 'update:modelValue', value: NotifiarrConfig): void;
  (e: 'test-connection'): void;
}>();

function updateField<K extends keyof NotifiarrConfig>(field: K, value: NotifiarrConfig[K]) {
  emit('update:modelValue', { ...props.modelValue, [field]: value });
}

const hasApiKey = computed(() => !!props.modelValue.apikey);
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-start justify-between">
      <div>
        <div class="flex items-center gap-2">
          <span class="text-2xl">🔔</span>
          <h3 class="text-lg font-semibold">Notifiarr Configuration</h3>
          <span class="text-xs px-2 py-0.5 rounded bg-surface-tertiary text-content-muted font-medium">Optional</span>
        </div>
        <p class="mt-1 text-sm text-content-secondary">
          Connect Notifiarr to receive notifications about Kometa runs and sync status.
        </p>
      </div>
      <a
        href="https://kometa.wiki/en/latest/config/notifiarr/"
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
      :class="hasApiKey ? 'bg-success/10 border border-success/20' : 'bg-surface-tertiary'"
    >
      <div class="flex items-center gap-3">
        <span :class="hasApiKey ? 'text-success' : 'text-content-muted'" class="text-xl">
          {{ hasApiKey ? '✓' : '🔔' }}
        </span>
        <div class="flex-1">
          <p class="font-medium" :class="hasApiKey ? 'text-success' : 'text-content'">
            {{ hasApiKey ? 'Notifiarr Connected' : 'Connect Notifiarr' }}
          </p>
          <p class="text-sm text-content-secondary">
            {{ hasApiKey
              ? 'Your Notifiarr API key is configured.'
              : 'Enter your Notifiarr API key to enable notifications.' }}
          </p>
        </div>
      </div>
    </div>

    <!-- API Key -->
    <div>
      <FormField
        label="API Key"
        required
        tooltip="Your Notifiarr API key from the Notifiarr website"
        help="Get your API key from notifiarr.com"
      >
        <Input
          type="password"
          :model-value="props.modelValue.apikey || ''"
          placeholder="Your Notifiarr API key"
          @update:model-value="updateField('apikey', $event)"
        />
      </FormField>
    </div>

    <!-- Test Connection -->
    <div v-if="hasApiKey" class="flex items-center gap-4 p-4 rounded-lg bg-surface-tertiary">
      <button
        class="px-4 py-2 rounded-lg bg-kometa-gold text-black font-medium hover:bg-kometa-gold/90 transition-colors"
        @click="emit('test-connection')"
      >
        Test Connection
      </button>
      <span class="text-sm text-content-secondary">
        Send a test notification to verify your setup
      </span>
    </div>

    <!-- Notification Settings -->
    <div class="border-t border-border pt-6">
      <h4 class="font-medium mb-4 flex items-center gap-2">
        <span>⚡</span> Notification Events
      </h4>
      <p class="text-sm text-content-secondary mb-4">
        Choose which events trigger notifications.
      </p>

      <div class="space-y-3">
        <Checkbox
          :model-value="props.modelValue.run_start_notify ?? true"
          @update:model-value="updateField('run_start_notify', $event)"
        >
          <span class="font-medium">Run Start</span>
          <span class="text-content-secondary ml-2">Notify when a Kometa run begins</span>
        </Checkbox>

        <Checkbox
          :model-value="props.modelValue.run_end_notify ?? true"
          @update:model-value="updateField('run_end_notify', $event)"
        >
          <span class="font-medium">Run End</span>
          <span class="text-content-secondary ml-2">Notify when a Kometa run completes</span>
        </Checkbox>

        <Checkbox
          :model-value="props.modelValue.sync_notify ?? false"
          @update:model-value="updateField('sync_notify', $event)"
        >
          <span class="font-medium">Collection Sync</span>
          <span class="text-content-secondary ml-2">Notify on collection sync events</span>
        </Checkbox>

        <Checkbox
          :model-value="props.modelValue.error_notify ?? true"
          @update:model-value="updateField('error_notify', $event)"
        >
          <span class="font-medium">Errors</span>
          <span class="text-content-secondary ml-2">Notify when errors occur during runs</span>
        </Checkbox>
      </div>
    </div>

    <!-- How It Works -->
    <div class="border-t border-border pt-6">
      <h4 class="font-medium mb-4 flex items-center gap-2">
        <span>📚</span> About Notifiarr
      </h4>
      <div class="p-4 rounded-lg bg-surface-tertiary text-sm">
        <p class="text-content-secondary mb-3">
          Notifiarr is a notification routing service that supports:
        </p>
        <ul class="list-disc list-inside space-y-1 text-content-secondary">
          <li>Discord webhooks with rich embeds</li>
          <li>Telegram, Slack, and many other platforms</li>
          <li>Mobile push notifications</li>
          <li>Aggregated notifications from multiple services</li>
        </ul>
        <p class="mt-3">
          <a
            href="https://notifiarr.com"
            target="_blank"
            class="text-kometa-gold hover:underline"
          >
            Create a free account at notifiarr.com →
          </a>
        </p>
      </div>
    </div>
  </div>
</template>
