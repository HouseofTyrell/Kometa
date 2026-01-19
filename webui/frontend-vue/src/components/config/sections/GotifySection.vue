<script setup lang="ts">
import { computed } from 'vue';
import FormField from '../FormField.vue';
import { Input } from '@/components/common';

interface GotifyConfig {
  url?: string;
  token?: string;
}

interface Props {
  modelValue: GotifyConfig;
}

const props = defineProps<Props>();
const emit = defineEmits<{
  (e: 'update:modelValue', value: GotifyConfig): void;
  (e: 'test-connection'): void;
}>();

function updateField<K extends keyof GotifyConfig>(field: K, value: GotifyConfig[K]) {
  emit('update:modelValue', { ...props.modelValue, [field]: value });
}

const isConfigured = computed(() => !!props.modelValue.url && !!props.modelValue.token);
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-start justify-between">
      <div>
        <div class="flex items-center gap-2">
          <span class="text-2xl">📨</span>
          <h3 class="text-lg font-semibold">Gotify Configuration</h3>
          <span class="text-xs px-2 py-0.5 rounded bg-surface-tertiary text-content-muted font-medium">Optional</span>
        </div>
        <p class="mt-1 text-sm text-content-secondary">
          Connect Gotify for self-hosted push notifications about Kometa runs.
        </p>
      </div>
      <a
        href="https://kometa.wiki/en/latest/config/gotify/"
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
          {{ isConfigured ? '✓' : '📨' }}
        </span>
        <div class="flex-1">
          <p class="font-medium" :class="isConfigured ? 'text-success' : 'text-content'">
            {{ isConfigured ? 'Gotify Connected' : 'Connect Gotify' }}
          </p>
          <p class="text-sm text-content-secondary">
            {{ isConfigured
              ? 'Your Gotify server is configured.'
              : 'Enter your Gotify server URL and application token.' }}
          </p>
        </div>
      </div>
    </div>

    <!-- Connection Settings -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <FormField
        label="Gotify URL"
        required
        tooltip="The URL to your Gotify server"
        help="e.g., https://gotify.example.com"
      >
        <Input
          :model-value="props.modelValue.url || ''"
          placeholder="https://gotify.example.com"
          @update:model-value="updateField('url', $event)"
        />
      </FormField>

      <FormField
        label="Application Token"
        required
        tooltip="Gotify application token for sending messages"
        help="Create an app in Gotify and copy its token"
      >
        <Input
          type="password"
          :model-value="props.modelValue.token || ''"
          placeholder="Your Gotify app token"
          @update:model-value="updateField('token', $event)"
        />
      </FormField>
    </div>

    <!-- Test Connection -->
    <div v-if="isConfigured" class="flex items-center gap-4 p-4 rounded-lg bg-surface-tertiary">
      <button
        class="px-4 py-2 rounded-lg bg-kometa-gold text-black font-medium hover:bg-kometa-gold/90 transition-colors"
        @click="emit('test-connection')"
      >
        Test Connection
      </button>
      <span class="text-sm text-content-secondary">
        Send a test notification to your Gotify server
      </span>
    </div>

    <!-- How to Get Token -->
    <div class="border-t border-border pt-6">
      <h4 class="font-medium mb-4 flex items-center gap-2">
        <span>🔑</span> Getting Your Application Token
      </h4>
      <div class="p-4 rounded-lg bg-surface-tertiary text-sm">
        <ol class="list-decimal list-inside space-y-2 text-content-secondary">
          <li>Log into your Gotify web interface</li>
          <li>Go to Apps in the sidebar</li>
          <li>Click "Create Application"</li>
          <li>Give it a name like "Kometa"</li>
          <li>Copy the generated token</li>
        </ol>
      </div>
    </div>

    <!-- About Gotify -->
    <div class="border-t border-border pt-6">
      <h4 class="font-medium mb-4 flex items-center gap-2">
        <span>💡</span> About Gotify
      </h4>
      <div class="p-4 rounded-lg bg-surface-tertiary text-sm">
        <p class="text-content-secondary mb-3">
          Gotify is a self-hosted push notification server:
        </p>
        <ul class="list-disc list-inside space-y-1 text-content-secondary">
          <li>100% self-hosted - your data stays on your server</li>
          <li>Android app available for mobile notifications</li>
          <li>Web interface for viewing messages</li>
          <li>Simple REST API for sending notifications</li>
          <li>No external dependencies or accounts needed</li>
        </ul>
        <p class="mt-3">
          <a
            href="https://gotify.net"
            target="_blank"
            class="text-kometa-gold hover:underline"
          >
            Learn more at gotify.net →
          </a>
        </p>
      </div>
    </div>
  </div>
</template>
