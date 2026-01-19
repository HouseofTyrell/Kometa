<script setup lang="ts">
import { computed } from 'vue';
import FormField from '../FormField.vue';
import { Input } from '@/components/common';

interface NtfyConfig {
  url?: string;
  topic?: string;
  token?: string;
}

interface Props {
  modelValue: NtfyConfig;
}

const props = defineProps<Props>();
const emit = defineEmits<{
  (e: 'update:modelValue', value: NtfyConfig): void;
  (e: 'test-connection'): void;
}>();

function updateField<K extends keyof NtfyConfig>(field: K, value: NtfyConfig[K]) {
  emit('update:modelValue', { ...props.modelValue, [field]: value });
}

const isConfigured = computed(() => !!props.modelValue.topic);
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-start justify-between">
      <div>
        <div class="flex items-center gap-2">
          <span class="text-2xl">🔔</span>
          <h3 class="text-lg font-semibold">ntfy Configuration</h3>
          <span class="text-xs px-2 py-0.5 rounded bg-surface-tertiary text-content-muted font-medium">Optional</span>
        </div>
        <p class="mt-1 text-sm text-content-secondary">
          Connect ntfy for simple HTTP-based push notifications. Use ntfy.sh or your own server.
        </p>
      </div>
      <a
        href="https://kometa.wiki/en/latest/config/ntfy/"
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
          {{ isConfigured ? '✓' : '🔔' }}
        </span>
        <div class="flex-1">
          <p class="font-medium" :class="isConfigured ? 'text-success' : 'text-content'">
            {{ isConfigured ? 'ntfy Configured' : 'Configure ntfy' }}
          </p>
          <p class="text-sm text-content-secondary">
            {{ isConfigured
              ? `Notifications will be sent to topic: ${props.modelValue.topic}`
              : 'Enter your ntfy topic to receive push notifications.' }}
          </p>
        </div>
      </div>
    </div>

    <!-- Connection Settings -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <FormField
        label="Topic"
        required
        tooltip="The ntfy topic to send notifications to"
        help="Use a unique, hard-to-guess topic name"
      >
        <Input
          :model-value="props.modelValue.topic || ''"
          placeholder="my-kometa-notifications"
          @update:model-value="updateField('topic', $event)"
        />
      </FormField>

      <FormField
        label="Server URL"
        tooltip="Custom ntfy server URL (leave empty for ntfy.sh)"
        help="Default: https://ntfy.sh"
      >
        <Input
          :model-value="props.modelValue.url || ''"
          placeholder="https://ntfy.sh"
          @update:model-value="updateField('url', $event)"
        />
      </FormField>
    </div>

    <!-- Access Token (optional) -->
    <FormField
      label="Access Token"
      tooltip="Authentication token for protected topics"
      help="Required if your topic requires authentication"
    >
      <Input
        type="password"
        :model-value="props.modelValue.token || ''"
        placeholder="tk_xxxxxxxxxxxxxxxx (optional)"
        @update:model-value="updateField('token', $event)"
      />
    </FormField>

    <!-- Test Connection -->
    <div v-if="isConfigured" class="flex items-center gap-4 p-4 rounded-lg bg-surface-tertiary">
      <button
        class="px-4 py-2 rounded-lg bg-kometa-gold text-black font-medium hover:bg-kometa-gold/90 transition-colors"
        @click="emit('test-connection')"
      >
        Test Notification
      </button>
      <span class="text-sm text-content-secondary">
        Send a test message to your ntfy topic
      </span>
    </div>

    <!-- Topic Security Notice -->
    <div class="p-4 rounded-lg bg-warning/10 border border-warning/20">
      <p class="text-warning font-medium flex items-center gap-2">
        <span>🔐</span> Topic Security
      </p>
      <p class="text-content-secondary text-sm mt-1">
        Anyone who knows your topic name can subscribe to it (on public ntfy servers).
        Use a long, random topic name or set up authentication with an access token.
      </p>
    </div>

    <!-- Quick Start -->
    <div class="border-t border-border pt-6">
      <h4 class="font-medium mb-4 flex items-center gap-2">
        <span>🚀</span> Quick Start
      </h4>
      <div class="p-4 rounded-lg bg-surface-tertiary text-sm">
        <p class="text-content-secondary mb-3">
          Subscribe to notifications on your device:
        </p>
        <div class="space-y-2">
          <div class="flex items-center gap-2">
            <span class="text-lg">📱</span>
            <span>Install the ntfy app from Play Store or App Store</span>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-lg">🔔</span>
            <span>Subscribe to your topic name</span>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-lg">✅</span>
            <span>Receive notifications when Kometa runs</span>
          </div>
        </div>
      </div>
    </div>

    <!-- About ntfy -->
    <div class="border-t border-border pt-6">
      <h4 class="font-medium mb-4 flex items-center gap-2">
        <span>💡</span> About ntfy
      </h4>
      <div class="p-4 rounded-lg bg-surface-tertiary text-sm">
        <p class="text-content-secondary mb-3">
          ntfy is a simple HTTP-based pub-sub notification service:
        </p>
        <ul class="list-disc list-inside space-y-1 text-content-secondary">
          <li>Free to use with ntfy.sh public server</li>
          <li>Can be self-hosted for privacy</li>
          <li>Mobile apps for iOS and Android</li>
          <li>Web UI for viewing notifications</li>
          <li>No account required for basic usage</li>
          <li>Supports email forwarding, webhooks, and more</li>
        </ul>
        <p class="mt-3">
          <a
            href="https://ntfy.sh"
            target="_blank"
            class="text-kometa-gold hover:underline"
          >
            Learn more at ntfy.sh →
          </a>
        </p>
      </div>
    </div>
  </div>
</template>
