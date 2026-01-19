<script setup lang="ts">
import { computed } from 'vue';
import FormField from '../FormField.vue';
import { Input, Checkbox, Select } from '@/components/common';

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

function updateField<K extends keyof RadarrConfig>(field: K, value: RadarrConfig[K]) {
  emit('update:modelValue', { ...props.modelValue, [field]: value });
}

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
    <div class="flex items-start justify-between">
      <div>
        <div class="flex items-center gap-2">
          <span class="text-2xl">🎥</span>
          <h3 class="text-lg font-semibold">Radarr Configuration</h3>
          <span class="text-xs px-2 py-0.5 rounded bg-surface-tertiary text-content-muted font-medium">Optional</span>
        </div>
        <p class="mt-1 text-sm text-content-secondary">
          Connect Radarr for automatic movie library management and missing movie additions.
        </p>
      </div>
      <a
        href="https://kometa.wiki/en/latest/config/radarr/"
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
    <div class="flex items-center gap-4 p-4 rounded-lg bg-surface-tertiary">
      <button
        class="px-4 py-2 rounded-lg bg-kometa-gold text-black font-medium hover:bg-kometa-gold/90 transition-colors"
        @click="emit('test-connection')"
      >
        Test Connection
      </button>
      <span class="text-sm text-content-secondary">
        Verify your Radarr instance is accessible
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
