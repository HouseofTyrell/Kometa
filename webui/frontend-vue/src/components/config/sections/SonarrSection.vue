<script setup lang="ts">
import { computed } from 'vue';
import FormField from '../FormField.vue';
import { Input, Checkbox, Select } from '@/components/common';

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

function updateField<K extends keyof SonarrConfig>(field: K, value: SonarrConfig[K]) {
  emit('update:modelValue', { ...props.modelValue, [field]: value });
}

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
    <div class="flex items-start justify-between">
      <div>
        <div class="flex items-center gap-2">
          <span class="text-2xl">📺</span>
          <h3 class="text-lg font-semibold">Sonarr Configuration</h3>
          <span class="text-xs px-2 py-0.5 rounded bg-surface-tertiary text-content-muted font-medium">Optional</span>
        </div>
        <p class="mt-1 text-sm text-content-secondary">
          Connect Sonarr for automatic TV show library management and missing episode additions.
        </p>
      </div>
      <a
        href="https://kometa.wiki/en/latest/config/sonarr/"
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
    <div class="flex items-center gap-4 p-4 rounded-lg bg-surface-tertiary">
      <button
        class="px-4 py-2 rounded-lg bg-kometa-gold text-black font-medium hover:bg-kometa-gold/90 transition-colors"
        @click="emit('test-connection')"
      >
        Test Connection
      </button>
      <span class="text-sm text-content-secondary">
        Verify your Sonarr instance is accessible
      </span>
    </div>

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
