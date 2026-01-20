<script setup lang="ts">
import { computed } from 'vue';
import FormField from '../FormField.vue';
import SectionHeader from '../SectionHeader.vue';
import TestConnectionButton from '../TestConnectionButton.vue';
import { Input } from '@/components/common';
import { useConfigSection } from '@/composables';
import { useConnectionsStore } from '@/stores';

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

const { updateField } = useConfigSection<TautulliConfig>(props, emit);
const connections = useConnectionsStore();

const isConfigured = computed(() => !!props.modelValue.url && !!props.modelValue.apikey);
const connectionStatus = computed(() => connections.getStatus('tautulli'));
const isConnected = computed(() => connections.isConnected('tautulli'));
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <SectionHeader
      icon="📊"
      title="Tautulli Configuration"
      description="Connect Tautulli for watch history and popularity-based collection builders."
      docs-url="https://kometa.wiki/en/latest/config/tautulli/"
      optional
    />

    <!-- Connection Status -->
    <div
      class="p-4 rounded-lg"
      :class="[
        isConnected ? 'bg-success/10 border border-success/20' :
        connectionStatus?.tested && !connectionStatus?.success ? 'bg-error/10 border border-error/20' :
        'bg-surface-tertiary'
      ]"
    >
      <div class="flex items-center gap-3">
        <span
          :class="[
            isConnected ? 'text-success' :
            connectionStatus?.tested && !connectionStatus?.success ? 'text-error' :
            'text-content-muted'
          ]"
          class="text-xl"
        >
          {{ isConnected ? '✓' : connectionStatus?.tested && !connectionStatus?.success ? '✗' : '📊' }}
        </span>
        <div class="flex-1">
          <p
            class="font-medium"
            :class="[
              isConnected ? 'text-success' :
              connectionStatus?.tested && !connectionStatus?.success ? 'text-error' :
              'text-content'
            ]"
          >
            {{ isConnected ? 'Tautulli Connected' :
               connectionStatus?.tested && !connectionStatus?.success ? 'Connection Failed' :
               isConfigured ? 'Not Tested' : 'Connect Tautulli' }}
          </p>
          <p class="text-sm text-content-secondary">
            {{ isConnected
              ? 'Your Tautulli instance is configured and verified.'
              : connectionStatus?.tested && !connectionStatus?.success
                ? connectionStatus?.message || 'Connection test failed. Check your URL and API key.'
                : isConfigured
                  ? 'Click "Test Connection" to verify your settings.'
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
    <TestConnectionButton
      description="Verify your Tautulli instance is accessible"
      @test="emit('test-connection')"
    />

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
