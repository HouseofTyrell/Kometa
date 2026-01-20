<script setup lang="ts">
import { computed } from 'vue';
import FormField from '../FormField.vue';
import SectionHeader from '../SectionHeader.vue';
import TestConnectionButton from '../TestConnectionButton.vue';
import { Input, Checkbox, Select } from '@/components/common';
import { useConfigSection } from '@/composables';
import { useConnectionsStore } from '@/stores';

interface SonarrConfig {
  url?: string;
  token?: string;
  add_missing?: boolean;
  add_existing?: boolean;
  upgrade_existing?: boolean;
  root_folder_path?: string;
  monitor?: string;
  quality_profile?: string;
  language_profile?: string;
  series_type?: string;
  season_folder?: boolean;
  tag?: string;
  search?: boolean;
  cutoff_search?: boolean;
  sonarr_path?: string;
  plex_path?: string;
}

interface Props {
  modelValue: SonarrConfig;
}

const props = defineProps<Props>();
const emit = defineEmits<{
  (e: 'update:modelValue', value: SonarrConfig): void;
  (e: 'test-connection'): void;
}>();

const { updateField } = useConfigSection<SonarrConfig>(props, emit);
const connections = useConnectionsStore();

const isConfigured = computed(() => !!props.modelValue.url && !!props.modelValue.token);
const connectionStatus = computed(() => connections.getStatus('sonarr'));
const isConnected = computed(() => connections.isConnected('sonarr'));

const monitorOptions = [
  { value: 'all', label: 'All Episodes' },
  { value: 'future', label: 'Future Episodes' },
  { value: 'missing', label: 'Missing Episodes' },
  { value: 'existing', label: 'Existing Episodes' },
  { value: 'pilot', label: 'Pilot Only' },
  { value: 'firstSeason', label: 'First Season' },
  { value: 'latestSeason', label: 'Latest Season' },
  { value: 'none', label: 'None' },
];

const seriesTypeOptions = [
  { value: 'standard', label: 'Standard' },
  { value: 'daily', label: 'Daily' },
  { value: 'anime', label: 'Anime' },
];
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <SectionHeader
      icon="📺"
      title="Sonarr Configuration"
      description="Connect Sonarr for automatic TV show library management and missing episode additions."
      docs-url="https://kometa.wiki/en/latest/config/sonarr/"
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
          {{ isConnected ? '✓' : connectionStatus?.tested && !connectionStatus?.success ? '✗' : '📺' }}
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
            {{ isConnected ? 'Sonarr Connected' :
               connectionStatus?.tested && !connectionStatus?.success ? 'Connection Failed' :
               isConfigured ? 'Not Tested' : 'Connect Sonarr' }}
          </p>
          <p class="text-sm text-content-secondary">
            {{ isConnected
              ? 'Your Sonarr instance is configured and verified.'
              : connectionStatus?.tested && !connectionStatus?.success
                ? connectionStatus?.message || 'Connection test failed. Check your URL and API token.'
                : isConfigured
                  ? 'Click "Test Connection" to verify your settings.'
                  : 'Enter your Sonarr URL and API token to enable TV show management.' }}
          </p>
        </div>
      </div>
    </div>

    <!-- Connection Settings -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <FormField
        label="Sonarr URL"
        required
        tooltip="The URL to your Sonarr instance"
        help="e.g., http://localhost:8989"
      >
        <Input
          :model-value="props.modelValue.url || ''"
          placeholder="http://localhost:8989"
          @update:model-value="updateField('url', $event)"
        />
      </FormField>

      <FormField
        label="API Token"
        required
        tooltip="Your Sonarr API key (Settings > General > API Key)"
      >
        <Input
          type="password"
          :model-value="props.modelValue.token || ''"
          placeholder="Your Sonarr API key"
          @update:model-value="updateField('token', $event)"
        />
      </FormField>
    </div>

    <!-- Test Connection -->
    <TestConnectionButton
      description="Verify your Sonarr instance is accessible"
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
          tooltip="The root folder path in Sonarr for new shows"
          help="Must match a root folder in Sonarr"
        >
          <Input
            :model-value="props.modelValue.root_folder_path || ''"
            placeholder="/tv"
            @update:model-value="updateField('root_folder_path', $event)"
          />
        </FormField>

        <FormField
          label="Quality Profile"
          tooltip="Quality profile to use for new shows"
          help="Must match a profile name in Sonarr"
        >
          <Input
            :model-value="props.modelValue.quality_profile || ''"
            placeholder="HD-1080p"
            @update:model-value="updateField('quality_profile', $event)"
          />
        </FormField>

        <FormField
          label="Language Profile"
          tooltip="Language profile for Sonarr v3"
          help="Required for Sonarr v3, optional for v4"
        >
          <Input
            :model-value="props.modelValue.language_profile || ''"
            placeholder="English"
            @update:model-value="updateField('language_profile', $event)"
          />
        </FormField>

        <FormField
          label="Monitor"
          tooltip="Which episodes to monitor"
        >
          <Select
            :model-value="props.modelValue.monitor || 'all'"
            :options="monitorOptions"
            @update:model-value="updateField('monitor', $event)"
          />
        </FormField>

        <FormField
          label="Series Type"
          tooltip="Type of series"
        >
          <Select
            :model-value="props.modelValue.series_type || 'standard'"
            :options="seriesTypeOptions"
            @update:model-value="updateField('series_type', $event)"
          />
        </FormField>

        <FormField
          label="Tag"
          tooltip="Tag to apply to shows added by Kometa"
          help="Optional - used to identify Kometa-added shows"
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
          <span class="text-content-secondary ml-2">Add missing shows from collections to Sonarr</span>
        </Checkbox>

        <Checkbox
          :model-value="props.modelValue.add_existing || false"
          @update:model-value="updateField('add_existing', $event)"
        >
          <span class="font-medium">Add Existing</span>
          <span class="text-content-secondary ml-2">Add existing Plex shows to Sonarr if not present</span>
        </Checkbox>

        <Checkbox
          :model-value="props.modelValue.upgrade_existing || false"
          @update:model-value="updateField('upgrade_existing', $event)"
        >
          <span class="font-medium">Upgrade Existing</span>
          <span class="text-content-secondary ml-2">Allow upgrades for existing shows in Sonarr</span>
        </Checkbox>

        <Checkbox
          :model-value="props.modelValue.season_folder || true"
          @update:model-value="updateField('season_folder', $event)"
        >
          <span class="font-medium">Season Folders</span>
          <span class="text-content-secondary ml-2">Use season folders for organization</span>
        </Checkbox>

        <Checkbox
          :model-value="props.modelValue.search || false"
          @update:model-value="updateField('search', $event)"
        >
          <span class="font-medium">Search on Add</span>
          <span class="text-content-secondary ml-2">Start searching for episodes when added</span>
        </Checkbox>

        <Checkbox
          :model-value="props.modelValue.cutoff_search || false"
          @update:model-value="updateField('cutoff_search', $event)"
        >
          <span class="font-medium">Cutoff Search</span>
          <span class="text-content-secondary ml-2">Search for cutoff unmet episodes</span>
        </Checkbox>
      </div>
    </div>

    <!-- Path Mapping -->
    <div class="border-t border-border pt-6">
      <h4 class="font-medium mb-4 flex items-center gap-2">
        <span>📁</span> Path Mapping
      </h4>
      <p class="text-sm text-content-secondary mb-4">
        Configure path mapping if Sonarr and Plex see files at different paths.
      </p>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <FormField
          label="Sonarr Path"
          tooltip="Path as seen by Sonarr"
          help="How Sonarr sees the TV files"
        >
          <Input
            :model-value="props.modelValue.sonarr_path || ''"
            placeholder="/tv"
            @update:model-value="updateField('sonarr_path', $event)"
          />
        </FormField>

        <FormField
          label="Plex Path"
          tooltip="Path as seen by Plex"
          help="How Plex sees the same TV files"
        >
          <Input
            :model-value="props.modelValue.plex_path || ''"
            placeholder="/data/tv"
            @update:model-value="updateField('plex_path', $event)"
          />
        </FormField>
      </div>
    </div>
  </div>
</template>
