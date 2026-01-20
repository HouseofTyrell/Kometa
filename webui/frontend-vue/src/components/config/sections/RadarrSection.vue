<script setup lang="ts">
import { computed } from 'vue';
import FormField from '../FormField.vue';
import SectionHeader from '../SectionHeader.vue';
import TestConnectionButton from '../TestConnectionButton.vue';
import { Input, Checkbox, Select } from '@/components/common';
import { useConfigSection } from '@/composables';
import { useConnectionsStore } from '@/stores';

interface RadarrConfig {
  url?: string;
  token?: string;
  add_missing?: boolean;
  add_existing?: boolean;
  upgrade_existing?: boolean;
  root_folder_path?: string;
  monitor?: boolean;
  availability?: string;
  quality_profile?: string;
  tag?: string;
  search?: boolean;
  radarr_path?: string;
  plex_path?: string;
}

interface Props {
  modelValue: RadarrConfig;
}

const props = defineProps<Props>();
const emit = defineEmits<{
  (e: 'update:modelValue', value: RadarrConfig): void;
  (e: 'test-connection'): void;
}>();

const { updateField } = useConfigSection<RadarrConfig>(props, emit);
const connections = useConnectionsStore();

const isConfigured = computed(() => !!props.modelValue.url && !!props.modelValue.token);
const connectionStatus = computed(() => connections.getStatus('radarr'));
const isConnected = computed(() => connections.isConnected('radarr'));

const availabilityOptions = [
  { value: 'announced', label: 'Announced' },
  { value: 'inCinemas', label: 'In Cinemas' },
  { value: 'released', label: 'Released' },
  { value: 'preDB', label: 'PreDB' },
];
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <SectionHeader
      icon="🎥"
      title="Radarr Configuration"
      description="Connect Radarr for automatic movie library management and missing movie additions."
      docs-url="https://kometa.wiki/en/latest/config/radarr/"
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
          {{ isConnected ? '✓' : connectionStatus?.tested && !connectionStatus?.success ? '✗' : '🎥' }}
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
            {{ isConnected ? 'Radarr Connected' :
               connectionStatus?.tested && !connectionStatus?.success ? 'Connection Failed' :
               isConfigured ? 'Not Tested' : 'Connect Radarr' }}
          </p>
          <p class="text-sm text-content-secondary">
            {{ isConnected
              ? 'Your Radarr instance is configured and verified.'
              : connectionStatus?.tested && !connectionStatus?.success
                ? connectionStatus?.message || 'Connection test failed. Check your URL and API token.'
                : isConfigured
                  ? 'Click "Test Connection" to verify your settings.'
                  : 'Enter your Radarr URL and API token to enable movie management.' }}
          </p>
        </div>
      </div>
    </div>

    <!-- Connection Settings -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <FormField
        label="Radarr URL"
        required
        tooltip="The URL to your Radarr instance"
        help="e.g., http://localhost:7878"
      >
        <Input
          :model-value="props.modelValue.url || ''"
          placeholder="http://localhost:7878"
          @update:model-value="updateField('url', $event)"
        />
      </FormField>

      <FormField
        label="API Token"
        required
        tooltip="Your Radarr API key (Settings > General > API Key)"
      >
        <Input
          type="password"
          :model-value="props.modelValue.token || ''"
          placeholder="Your Radarr API key"
          @update:model-value="updateField('token', $event)"
        />
      </FormField>
    </div>

    <!-- Test Connection -->
    <TestConnectionButton
      description="Verify your Radarr instance is accessible"
      @test="emit('test-connection')"
    />

    <!-- Import Settings -->
    <div class="border-t border-border pt-6">
      <h4 class="font-medium mb-4 flex items-center gap-2">
        <span>📥</span> Import Settings
      </h4>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <FormField
          label="Root Folder Path"
          tooltip="The root folder path in Radarr for new movies"
          help="Must match a root folder in Radarr"
        >
          <Input
            :model-value="props.modelValue.root_folder_path || ''"
            placeholder="/movies"
            @update:model-value="updateField('root_folder_path', $event)"
          />
        </FormField>

        <FormField
          label="Quality Profile"
          tooltip="Quality profile to use for new movies"
          help="Must match a profile name in Radarr"
        >
          <Input
            :model-value="props.modelValue.quality_profile || ''"
            placeholder="HD-1080p"
            @update:model-value="updateField('quality_profile', $event)"
          />
        </FormField>

        <FormField
          label="Availability"
          tooltip="When the movie should be available for download"
        >
          <Select
            :model-value="props.modelValue.availability || 'announced'"
            :options="availabilityOptions"
            @update:model-value="updateField('availability', $event)"
          />
        </FormField>

        <FormField
          label="Tag"
          tooltip="Tag to apply to movies added by Kometa"
          help="Optional - used to identify Kometa-added movies"
        >
          <Input
            :model-value="props.modelValue.tag || ''"
            placeholder="kometa"
            @update:model-value="updateField('tag', $event)"
          />
        </FormField>
      </div>

      <div class="space-y-3">
        <Checkbox
          :model-value="props.modelValue.add_missing || false"
          @update:model-value="updateField('add_missing', $event)"
        >
          <span class="font-medium">Add Missing</span>
          <span class="text-content-secondary ml-2">Add missing movies from collections to Radarr</span>
        </Checkbox>

        <Checkbox
          :model-value="props.modelValue.add_existing || false"
          @update:model-value="updateField('add_existing', $event)"
        >
          <span class="font-medium">Add Existing</span>
          <span class="text-content-secondary ml-2">Add existing Plex movies to Radarr if not present</span>
        </Checkbox>

        <Checkbox
          :model-value="props.modelValue.upgrade_existing || false"
          @update:model-value="updateField('upgrade_existing', $event)"
        >
          <span class="font-medium">Upgrade Existing</span>
          <span class="text-content-secondary ml-2">Allow upgrades for existing movies in Radarr</span>
        </Checkbox>

        <Checkbox
          :model-value="props.modelValue.monitor || true"
          @update:model-value="updateField('monitor', $event)"
        >
          <span class="font-medium">Monitor</span>
          <span class="text-content-secondary ml-2">Monitor added movies for downloads</span>
        </Checkbox>

        <Checkbox
          :model-value="props.modelValue.search || false"
          @update:model-value="updateField('search', $event)"
        >
          <span class="font-medium">Search on Add</span>
          <span class="text-content-secondary ml-2">Start searching for movies when added</span>
        </Checkbox>
      </div>
    </div>

    <!-- Path Mapping -->
    <div class="border-t border-border pt-6">
      <h4 class="font-medium mb-4 flex items-center gap-2">
        <span>📁</span> Path Mapping
      </h4>
      <p class="text-sm text-content-secondary mb-4">
        Configure path mapping if Radarr and Plex see files at different paths.
      </p>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <FormField
          label="Radarr Path"
          tooltip="Path as seen by Radarr"
          help="How Radarr sees the movie files"
        >
          <Input
            :model-value="props.modelValue.radarr_path || ''"
            placeholder="/movies"
            @update:model-value="updateField('radarr_path', $event)"
          />
        </FormField>

        <FormField
          label="Plex Path"
          tooltip="Path as seen by Plex"
          help="How Plex sees the same movie files"
        >
          <Input
            :model-value="props.modelValue.plex_path || ''"
            placeholder="/data/movies"
            @update:model-value="updateField('plex_path', $event)"
          />
        </FormField>
      </div>
    </div>
  </div>
</template>
