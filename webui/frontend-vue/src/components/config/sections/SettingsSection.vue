<script setup lang="ts">
import { computed } from 'vue';
import FormField from '../FormField.vue';
import { Input, Checkbox, Select } from '@/components/common';

interface SettingsConfig {
  cache?: string;
  cache_expiration?: number;
  asset_directory?: string;
  asset_folders?: boolean;
  asset_depth?: number;
  create_asset_folders?: boolean;
  prioritize_assets?: boolean;
  dimensional_asset_rename?: boolean;
  download_url_assets?: boolean;
  show_missing_season_assets?: boolean;
  show_missing_episode_assets?: boolean;
  show_asset_not_needed?: boolean;
  sync_mode?: string;
  default_collection_order?: string;
  minimum_items?: number;
  delete_below_minimum?: boolean;
  delete_not_scheduled?: boolean;
  run_again_delay?: number;
  missing_only_released?: boolean;
  only_filter_missing?: boolean;
  show_unmanaged?: boolean;
  show_unconfigured?: boolean;
  show_filtered?: boolean;
  show_options?: boolean;
  show_missing?: boolean;
  show_missing_assets?: boolean;
  save_report?: boolean;
  tvdb_language?: string;
  ignore_ids?: string[];
  ignore_imdb_ids?: string[];
  item_refresh_delay?: number;
  playlist_sync_to_users?: string;
  playlist_exclude_users?: string;
  playlist_report?: boolean;
  verify_ssl?: boolean;
  check_nightly?: boolean;
}

interface Props {
  modelValue: SettingsConfig;
}

const props = defineProps<Props>();
const emit = defineEmits<{
  (e: 'update:modelValue', value: SettingsConfig): void;
}>();

function updateField<K extends keyof SettingsConfig>(field: K, value: SettingsConfig[K]) {
  emit('update:modelValue', { ...props.modelValue, [field]: value });
}

const syncModes = [
  { value: 'append', label: 'Append - Add items, never remove' },
  { value: 'sync', label: 'Sync - Add and remove items to match' },
];

const collectionOrders = [
  { value: 'release', label: 'Release Date' },
  { value: 'alpha', label: 'Alphabetical' },
  { value: 'custom', label: 'Custom Order' },
  { value: 'random', label: 'Random' },
];
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-start justify-between">
      <div>
        <div class="flex items-center gap-2">
          <span class="text-2xl">⚙️</span>
          <h3 class="text-lg font-semibold">Global Settings</h3>
          <span class="text-xs px-2 py-0.5 rounded bg-surface-tertiary text-content-muted font-medium">Optional</span>
        </div>
        <p class="mt-1 text-sm text-content-secondary">
          Configure global settings that apply to all libraries and runs.
        </p>
      </div>
      <a
        href="https://kometa.wiki/en/latest/config/settings/"
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

    <!-- Cache Settings -->
    <div class="border-t border-border pt-6">
      <h4 class="font-medium mb-4 flex items-center gap-2">
        <span>💾</span> Cache Settings
      </h4>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <FormField
          label="Cache Directory"
          default-value="config/cache"
          tooltip="Directory to store cached data"
          help="Path to the cache directory"
        >
          <Input
            :model-value="props.modelValue.cache || ''"
            placeholder="config/cache"
            @update:model-value="updateField('cache', $event)"
          />
        </FormField>

        <FormField
          label="Cache Expiration"
          default-value="60"
          tooltip="Number of days before cached data expires"
          help="Days before cache expires"
        >
          <Input
            type="number"
            :model-value="String(props.modelValue.cache_expiration || 60)"
            @update:model-value="updateField('cache_expiration', Number($event))"
            min="1"
            max="365"
          />
        </FormField>
      </div>
    </div>

    <!-- Asset Settings -->
    <div class="border-t border-border pt-6">
      <h4 class="font-medium mb-4 flex items-center gap-2">
        <span>🖼️</span> Asset Settings
      </h4>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <FormField
          label="Asset Directory"
          tooltip="Directory where poster and background assets are stored"
          help="Path to your assets folder"
        >
          <Input
            :model-value="props.modelValue.asset_directory || ''"
            placeholder="config/assets"
            @update:model-value="updateField('asset_directory', $event)"
          />
        </FormField>

        <FormField
          label="Asset Depth"
          default-value="0"
          tooltip="How many folder levels deep to search for assets"
          help="Folder depth for asset search"
        >
          <Input
            type="number"
            :model-value="String(props.modelValue.asset_depth || 0)"
            @update:model-value="updateField('asset_depth', Number($event))"
            min="0"
            max="10"
          />
        </FormField>
      </div>

      <div class="space-y-3">
        <Checkbox
          :model-value="props.modelValue.asset_folders || false"
          @update:model-value="updateField('asset_folders', $event)"
        >
          <span class="font-medium">Asset Folders</span>
          <span class="text-content-secondary ml-2">Use folder-based asset organization</span>
        </Checkbox>

        <Checkbox
          :model-value="props.modelValue.create_asset_folders || false"
          @update:model-value="updateField('create_asset_folders', $event)"
        >
          <span class="font-medium">Create Asset Folders</span>
          <span class="text-content-secondary ml-2">Automatically create asset folders for items</span>
        </Checkbox>

        <Checkbox
          :model-value="props.modelValue.prioritize_assets || false"
          @update:model-value="updateField('prioritize_assets', $event)"
        >
          <span class="font-medium">Prioritize Assets</span>
          <span class="text-content-secondary ml-2">Prefer local assets over online sources</span>
        </Checkbox>

        <Checkbox
          :model-value="props.modelValue.download_url_assets || false"
          @update:model-value="updateField('download_url_assets', $event)"
        >
          <span class="font-medium">Download URL Assets</span>
          <span class="text-content-secondary ml-2">Download assets from URLs to local storage</span>
        </Checkbox>
      </div>
    </div>

    <!-- Collection Settings -->
    <div class="border-t border-border pt-6">
      <h4 class="font-medium mb-4 flex items-center gap-2">
        <span>📚</span> Collection Settings
      </h4>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <FormField
          label="Sync Mode"
          default-value="append"
          tooltip="How to handle items in collections"
        >
          <Select
            :model-value="props.modelValue.sync_mode || 'append'"
            :options="syncModes"
            @update:model-value="updateField('sync_mode', $event)"
          />
        </FormField>

        <FormField
          label="Default Collection Order"
          default-value="release"
          tooltip="Default sort order for collections"
        >
          <Select
            :model-value="props.modelValue.default_collection_order || 'release'"
            :options="collectionOrders"
            @update:model-value="updateField('default_collection_order', $event)"
          />
        </FormField>

        <FormField
          label="Minimum Items"
          default-value="1"
          tooltip="Minimum items required to create a collection"
          help="Collections with fewer items won't be created"
        >
          <Input
            type="number"
            :model-value="String(props.modelValue.minimum_items || 1)"
            @update:model-value="updateField('minimum_items', Number($event))"
            min="1"
          />
        </FormField>

        <FormField
          label="Run Again Delay"
          default-value="0"
          tooltip="Minutes to wait before running again"
          help="Delay between runs in minutes"
        >
          <Input
            type="number"
            :model-value="String(props.modelValue.run_again_delay || 0)"
            @update:model-value="updateField('run_again_delay', Number($event))"
            min="0"
          />
        </FormField>
      </div>

      <div class="space-y-3">
        <Checkbox
          :model-value="props.modelValue.delete_below_minimum || false"
          @update:model-value="updateField('delete_below_minimum', $event)"
        >
          <span class="font-medium">Delete Below Minimum</span>
          <span class="text-content-secondary ml-2">Delete collections that fall below minimum items</span>
        </Checkbox>

        <Checkbox
          :model-value="props.modelValue.delete_not_scheduled || false"
          @update:model-value="updateField('delete_not_scheduled', $event)"
        >
          <span class="font-medium">Delete Not Scheduled</span>
          <span class="text-content-secondary ml-2">Delete collections not scheduled to run</span>
        </Checkbox>
      </div>
    </div>

    <!-- Display Settings -->
    <div class="border-t border-border pt-6">
      <h4 class="font-medium mb-4 flex items-center gap-2">
        <span>👁️</span> Display Settings
      </h4>

      <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
        <Checkbox
          :model-value="props.modelValue.show_unmanaged || false"
          @update:model-value="updateField('show_unmanaged', $event)"
        >
          <span>Show Unmanaged</span>
        </Checkbox>

        <Checkbox
          :model-value="props.modelValue.show_unconfigured || false"
          @update:model-value="updateField('show_unconfigured', $event)"
        >
          <span>Show Unconfigured</span>
        </Checkbox>

        <Checkbox
          :model-value="props.modelValue.show_filtered || false"
          @update:model-value="updateField('show_filtered', $event)"
        >
          <span>Show Filtered</span>
        </Checkbox>

        <Checkbox
          :model-value="props.modelValue.show_options || false"
          @update:model-value="updateField('show_options', $event)"
        >
          <span>Show Options</span>
        </Checkbox>

        <Checkbox
          :model-value="props.modelValue.show_missing || false"
          @update:model-value="updateField('show_missing', $event)"
        >
          <span>Show Missing</span>
        </Checkbox>

        <Checkbox
          :model-value="props.modelValue.show_missing_assets || false"
          @update:model-value="updateField('show_missing_assets', $event)"
        >
          <span>Show Missing Assets</span>
        </Checkbox>

        <Checkbox
          :model-value="props.modelValue.save_report || false"
          @update:model-value="updateField('save_report', $event)"
        >
          <span>Save Report</span>
        </Checkbox>
      </div>
    </div>

    <!-- Other Settings -->
    <div class="border-t border-border pt-6">
      <h4 class="font-medium mb-4 flex items-center gap-2">
        <span>🔧</span> Other Settings
      </h4>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <FormField
          label="Item Refresh Delay"
          default-value="0"
          tooltip="Seconds to wait between item refreshes"
          help="Delay between item refreshes"
        >
          <Input
            type="number"
            :model-value="String(props.modelValue.item_refresh_delay || 0)"
            @update:model-value="updateField('item_refresh_delay', Number($event))"
            min="0"
          />
        </FormField>

        <FormField
          label="TVDB Language"
          default-value="en"
          tooltip="Language for TVDB metadata"
          help="ISO language code"
        >
          <Input
            :model-value="props.modelValue.tvdb_language || 'en'"
            placeholder="en"
            @update:model-value="updateField('tvdb_language', $event)"
          />
        </FormField>
      </div>

      <div class="space-y-3">
        <Checkbox
          :model-value="props.modelValue.verify_ssl || true"
          @update:model-value="updateField('verify_ssl', $event)"
        >
          <span class="font-medium">Verify SSL</span>
          <span class="text-content-secondary ml-2">Verify SSL certificates for HTTPS connections</span>
        </Checkbox>

        <Checkbox
          :model-value="props.modelValue.check_nightly || false"
          @update:model-value="updateField('check_nightly', $event)"
        >
          <span class="font-medium">Check Nightly</span>
          <span class="text-content-secondary ml-2">Check for nightly builds instead of stable releases</span>
        </Checkbox>
      </div>
    </div>
  </div>
</template>
