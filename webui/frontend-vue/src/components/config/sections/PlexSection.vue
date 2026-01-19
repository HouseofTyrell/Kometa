<script setup lang="ts">
import FormField from '../FormField.vue';
import SectionHeader from '../SectionHeader.vue';
import TestConnectionButton from '../TestConnectionButton.vue';
import { Input, Checkbox } from '@/components/common';
import { useConfigSection } from '@/composables';

interface PlexConfig {
  url?: string;
  token?: string;
  timeout?: number;
  db_cache?: number;
  verify_ssl?: boolean;
  clean_bundles?: boolean;
  empty_trash?: boolean;
  optimize?: boolean;
}

interface Props {
  modelValue: PlexConfig;
}

const props = defineProps<Props>();
const emit = defineEmits<{
  (e: 'update:modelValue', value: PlexConfig): void;
  (e: 'test-connection'): void;
}>();

const { config, updateField } = useConfigSection<PlexConfig>(props, emit);
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <SectionHeader
      icon="📺"
      title="Plex Configuration"
      description="Connect Kometa to your Plex Media Server. The URL must be the direct server address, not app.plex.tv."
      docs-url="https://kometa.wiki/en/latest/config/plex/"
      required
    />

    <!-- Connection Settings -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="md:col-span-2">
        <FormField
          label="Plex URL"
          required
          tooltip="The direct URL to your Plex server. Use the local IP address if running in Docker."
          help="Direct URL to your Plex server (not app.plex.tv)"
        >
          <Input
            :model-value="config.url || ''"
            placeholder="http://192.168.1.100:32400"
            @update:model-value="updateField('url', $event)"
          />
        </FormField>
      </div>
      <FormField
        label="Timeout"
        default-value="60s"
        help="Seconds to wait for Plex responses"
      >
        <Input
          type="number"
          :model-value="String(config.timeout || 60)"
          @update:model-value="updateField('timeout', Number($event))"
          min="10"
          max="300"
        />
      </FormField>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="md:col-span-2">
        <FormField
          label="Plex Token"
          required
          tooltip="Authentication token for your Plex account. Required to access your server's API."
        >
          <Input
            type="password"
            :model-value="config.token || ''"
            placeholder="Your Plex token"
            @update:model-value="updateField('token', $event)"
          />
          <template #help>
            <a
              href="https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/"
              target="_blank"
              class="text-kometa-gold hover:underline"
            >
              How to find your token ↗
            </a>
          </template>
        </FormField>
      </div>
      <FormField
        label="DB Cache (MB)"
        default-value="40"
        help="Plex database cache size in megabytes"
      >
        <Input
          type="number"
          :model-value="String(config.db_cache || 40)"
          @update:model-value="updateField('db_cache', Number($event))"
          min="0"
        />
      </FormField>
    </div>

    <div>
      <Checkbox
        :model-value="config.verify_ssl || false"
        @update:model-value="updateField('verify_ssl', $event)"
      >
        <span class="font-medium">Verify SSL</span>
        <span class="text-content-secondary ml-2">Enable SSL certificate verification for HTTPS connections</span>
      </Checkbox>
    </div>

    <!-- Test Connection -->
    <TestConnectionButton
      description="Verify your Plex server is accessible with the provided credentials"
      @test="emit('test-connection')"
    />

    <!-- Maintenance Operations -->
    <div class="border-t border-border pt-6">
      <div class="flex items-center gap-2 mb-4">
        <span class="text-lg">🔧</span>
        <h4 class="font-medium">Maintenance Operations</h4>
      </div>
      <div class="p-3 rounded-lg bg-info/10 border border-info/20 mb-4">
        <div class="flex items-start gap-2">
          <span class="text-info">ℹ️</span>
          <p class="text-sm text-content-secondary">
            These operations run <strong class="text-content">after all collection files are processed</strong>.
            They can also accept schedule options instead of true/false.
          </p>
        </div>
      </div>

      <div class="space-y-3">
        <Checkbox
          :model-value="config.clean_bundles || false"
          @update:model-value="updateField('clean_bundles', $event)"
        >
          <span class="font-medium">Clean Bundles</span>
          <span class="text-content-secondary ml-2">Remove unused bundle files from Plex</span>
        </Checkbox>

        <Checkbox
          :model-value="config.empty_trash || false"
          @update:model-value="updateField('empty_trash', $event)"
        >
          <span class="font-medium">Empty Trash</span>
          <span class="text-content-secondary ml-2">Empty the trash for all Plex libraries</span>
        </Checkbox>

        <Checkbox
          :model-value="config.optimize || false"
          @update:model-value="updateField('optimize', $event)"
        >
          <span class="font-medium">Optimize Database</span>
          <span class="text-content-secondary ml-2">Optimize the Plex database</span>
        </Checkbox>
      </div>
    </div>
  </div>
</template>
