<script setup lang="ts">
import { computed } from 'vue';
import FormField from '../FormField.vue';
import { Checkbox, Card, Select } from '@/components/common';

interface OperationsConfig {
  // Mass Updates
  mass_genre_update?: string;
  mass_content_rating_update?: string;
  mass_audience_rating_update?: string;
  mass_critic_rating_update?: string;
  mass_user_rating_update?: string;
  mass_originally_available_update?: string;
  mass_studio_update?: string;
  mass_poster_update?: string;
  mass_background_update?: string;

  // Split/Merge
  split_duplicates?: boolean;
  radarr_add_missing?: boolean;
  radarr_remove_by_tag?: string;
  sonarr_add_missing?: boolean;
  sonarr_remove_by_tag?: string;

  // Metadata
  update_blank_track_titles?: boolean;
  remove_title_parentheses?: boolean;

  // Assets
  assets_for_all?: boolean;
  delete_unmanaged_collections?: boolean;
  delete_collections_with_less?: number;

  // Genre Operations
  genre_mapper?: Record<string, string>;
  content_rating_mapper?: Record<string, string>;
}

interface Props {
  modelValue: OperationsConfig;
}

const props = defineProps<Props>();
const emit = defineEmits<{
  (e: 'update:modelValue', value: OperationsConfig): void;
}>();

function updateField<K extends keyof OperationsConfig>(field: K, value: OperationsConfig[K]) {
  emit('update:modelValue', { ...props.modelValue, [field]: value });
}

const updateSources = [
  { value: '', label: 'None' },
  { value: 'tmdb', label: 'TMDb' },
  { value: 'imdb', label: 'IMDb' },
  { value: 'trakt', label: 'Trakt' },
  { value: 'tvdb', label: 'TVDB' },
  { value: 'omdb', label: 'OMDb' },
  { value: 'mdb', label: 'MDb' },
  { value: 'anidb', label: 'AniDB' },
  { value: 'mal', label: 'MyAnimeList' },
];

const ratingUpdateSources = [
  { value: '', label: 'None' },
  { value: 'tmdb', label: 'TMDb' },
  { value: 'imdb', label: 'IMDb' },
  { value: 'trakt_user', label: 'Trakt User' },
  { value: 'omdb', label: 'OMDb' },
  { value: 'mdb', label: 'MDb' },
  { value: 'mdb_average', label: 'MDb Average' },
  { value: 'mdb_imdb', label: 'MDb IMDb' },
  { value: 'mdb_metacritic', label: 'MDb Metacritic' },
  { value: 'mdb_metacriticuser', label: 'MDb Metacritic User' },
  { value: 'mdb_trakt', label: 'MDb Trakt' },
  { value: 'mdb_tomatoes', label: 'MDb Rotten Tomatoes' },
  { value: 'mdb_tomatoesaudience', label: 'MDb RT Audience' },
  { value: 'mdb_tmdb', label: 'MDb TMDb' },
  { value: 'mdb_letterboxd', label: 'MDb Letterboxd' },
  { value: 'anidb_rating', label: 'AniDB Rating' },
  { value: 'anidb_average', label: 'AniDB Average' },
  { value: 'anidb_score', label: 'AniDB Score' },
  { value: 'mal_score', label: 'MAL Score' },
];

const posterSources = [
  { value: '', label: 'None' },
  { value: 'tmdb', label: 'TMDb' },
  { value: 'plex', label: 'Plex' },
  { value: 'lock', label: 'Lock Current' },
  { value: 'unlock', label: 'Unlock' },
];
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-start justify-between">
      <div>
        <div class="flex items-center gap-2">
          <span class="text-2xl">⚡</span>
          <h3 class="text-lg font-semibold">Operations</h3>
          <span class="text-xs px-2 py-0.5 rounded bg-surface-tertiary text-content-muted font-medium">Optional</span>
        </div>
        <p class="mt-1 text-sm text-content-secondary">
          Configure mass operations for updating metadata across your libraries.
        </p>
      </div>
      <a
        href="https://kometa.wiki/en/latest/config/operations/"
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

    <!-- Info Box -->
    <div class="p-3 rounded-lg bg-info/10 border border-info/20">
      <div class="flex items-start gap-2">
        <span class="text-info">ℹ️</span>
        <p class="text-sm text-content-secondary">
          Operations run on <strong class="text-content">all items in a library</strong>.
          They can be configured globally here or per-library in the Libraries section.
        </p>
      </div>
    </div>

    <!-- Mass Update Operations -->
    <div class="border-t border-border pt-6">
      <h4 class="font-medium mb-4 flex items-center gap-2">
        <span>🔄</span> Mass Update Operations
      </h4>
      <p class="text-sm text-content-secondary mb-4">
        Update metadata fields from external sources.
      </p>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <FormField label="Mass Genre Update" help="Source for genre metadata">
          <Select
            :model-value="props.modelValue.mass_genre_update || ''"
            :options="updateSources"
            @update:model-value="updateField('mass_genre_update', $event)"
          />
        </FormField>

        <FormField label="Mass Content Rating Update" help="Source for content ratings">
          <Select
            :model-value="props.modelValue.mass_content_rating_update || ''"
            :options="updateSources"
            @update:model-value="updateField('mass_content_rating_update', $event)"
          />
        </FormField>

        <FormField label="Mass Audience Rating Update" help="Source for audience ratings">
          <Select
            :model-value="props.modelValue.mass_audience_rating_update || ''"
            :options="ratingUpdateSources"
            @update:model-value="updateField('mass_audience_rating_update', $event)"
          />
        </FormField>

        <FormField label="Mass Critic Rating Update" help="Source for critic ratings">
          <Select
            :model-value="props.modelValue.mass_critic_rating_update || ''"
            :options="ratingUpdateSources"
            @update:model-value="updateField('mass_critic_rating_update', $event)"
          />
        </FormField>

        <FormField label="Mass Poster Update" help="Source for poster images">
          <Select
            :model-value="props.modelValue.mass_poster_update || ''"
            :options="posterSources"
            @update:model-value="updateField('mass_poster_update', $event)"
          />
        </FormField>

        <FormField label="Mass Background Update" help="Source for background images">
          <Select
            :model-value="props.modelValue.mass_background_update || ''"
            :options="posterSources"
            @update:model-value="updateField('mass_background_update', $event)"
          />
        </FormField>
      </div>
    </div>

    <!-- Title Operations -->
    <div class="border-t border-border pt-6">
      <h4 class="font-medium mb-4 flex items-center gap-2">
        <span>📝</span> Title Operations
      </h4>

      <div class="space-y-3">
        <Checkbox
          :model-value="props.modelValue.split_duplicates || false"
          @update:model-value="updateField('split_duplicates', $event)"
        >
          <span class="font-medium">Split Duplicates</span>
          <span class="text-content-secondary ml-2">Separate items that share the same title</span>
        </Checkbox>

        <Checkbox
          :model-value="props.modelValue.remove_title_parentheses || false"
          @update:model-value="updateField('remove_title_parentheses', $event)"
        >
          <span class="font-medium">Remove Title Parentheses</span>
          <span class="text-content-secondary ml-2">Remove year and other parenthetical text from titles</span>
        </Checkbox>

        <Checkbox
          :model-value="props.modelValue.update_blank_track_titles || false"
          @update:model-value="updateField('update_blank_track_titles', $event)"
        >
          <span class="font-medium">Update Blank Track Titles</span>
          <span class="text-content-secondary ml-2">Fill in missing track titles for music libraries</span>
        </Checkbox>
      </div>
    </div>

    <!-- Arr Integration Operations -->
    <div class="border-t border-border pt-6">
      <h4 class="font-medium mb-4 flex items-center gap-2">
        <span>📥</span> Arr Integration Operations
      </h4>

      <div class="space-y-3">
        <Checkbox
          :model-value="props.modelValue.radarr_add_missing || false"
          @update:model-value="updateField('radarr_add_missing', $event)"
        >
          <span class="font-medium">Radarr Add Missing</span>
          <span class="text-content-secondary ml-2">Add missing movies to Radarr</span>
        </Checkbox>

        <Checkbox
          :model-value="props.modelValue.sonarr_add_missing || false"
          @update:model-value="updateField('sonarr_add_missing', $event)"
        >
          <span class="font-medium">Sonarr Add Missing</span>
          <span class="text-content-secondary ml-2">Add missing shows to Sonarr</span>
        </Checkbox>
      </div>
    </div>

    <!-- Asset & Collection Operations -->
    <div class="border-t border-border pt-6">
      <h4 class="font-medium mb-4 flex items-center gap-2">
        <span>🗂️</span> Asset & Collection Operations
      </h4>

      <div class="space-y-3">
        <Checkbox
          :model-value="props.modelValue.assets_for_all || false"
          @update:model-value="updateField('assets_for_all', $event)"
        >
          <span class="font-medium">Assets For All</span>
          <span class="text-content-secondary ml-2">Search for assets for all items, not just collections</span>
        </Checkbox>

        <Checkbox
          :model-value="props.modelValue.delete_unmanaged_collections || false"
          @update:model-value="updateField('delete_unmanaged_collections', $event)"
        >
          <span class="font-medium">Delete Unmanaged Collections</span>
          <span class="text-content-secondary ml-2">Remove collections not managed by Kometa</span>
        </Checkbox>
      </div>

      <div class="mt-4">
        <FormField
          label="Delete Collections With Less Than"
          default-value="0"
          tooltip="Delete collections with fewer items than this number (0 = disabled)"
          help="Minimum items to keep a collection"
        >
          <input
            type="number"
            :value="props.modelValue.delete_collections_with_less || 0"
            class="w-full px-3 py-2 rounded-lg bg-surface-primary border border-border
                   focus:border-kometa-gold focus:ring-1 focus:ring-kometa-gold"
            min="0"
            @input="updateField('delete_collections_with_less', Number(($event.target as HTMLInputElement).value))"
          />
        </FormField>
      </div>
    </div>
  </div>
</template>
