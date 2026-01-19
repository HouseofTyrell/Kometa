<script setup lang="ts">
import { ref, computed } from 'vue';
import FormField from '../FormField.vue';
import { Input, Button, Card, Badge, Modal, Checkbox, Select } from '@/components/common';

interface CollectionFile {
  file?: string;
  default?: string;
  template_variables?: Record<string, unknown>;
}

interface LibraryOperations {
  split_duplicates?: boolean;
  assets_for_all?: boolean;
  delete_collections?: {
    configured?: boolean;
    managed?: boolean;
    less?: number;
  };
  mass_genre_update?: string;
  mass_content_rating_update?: string;
  mass_audience_rating_update?: string;
  mass_critic_rating_update?: string;
  mass_user_rating_update?: string;
  mass_originally_available_update?: string;
  mass_poster_update?: string;
  mass_background_update?: string;
  radarr_add_all?: boolean;
  radarr_remove_by_tag?: string;
  sonarr_add_all?: boolean;
  sonarr_remove_by_tag?: string;
}

interface LibraryConfig {
  collection_files?: (string | CollectionFile)[];
  overlay_files?: (string | CollectionFile)[];
  metadata_files?: (string | CollectionFile)[];
  operations?: LibraryOperations;
  schedule?: string;
  report_path?: string;
  template_variables?: Record<string, unknown>;
  filters?: Record<string, unknown>;
  run_order?: string[];
  delete_unmanaged_collections?: boolean;
  delete_collections_with_less?: number;
  asset_directory?: string;
}

interface Props {
  modelValue: Record<string, LibraryConfig>;
}

const props = defineProps<Props>();
const emit = defineEmits<{
  (e: 'update:modelValue', value: Record<string, LibraryConfig>): void;
}>();

const showAddModal = ref(false);
const newLibraryName = ref('');
const editingLibrary = ref<string | null>(null);
const activeTab = ref<Record<string, string>>({});

// File input states
const newCollectionFile = ref<Record<string, string>>({});
const newOverlayFile = ref<Record<string, string>>({});
const newMetadataFile = ref<Record<string, string>>({});

const libraries = computed(() => Object.entries(props.modelValue || {}));

// Default collection options from Kometa
const defaultCollectionOptions = [
  { value: '', label: 'Custom file path...' },
  { value: 'basic', label: 'Basic (New, Top Rated, etc.)' },
  { value: 'imdb', label: 'IMDb (Top 250, Popular, etc.)' },
  { value: 'trakt', label: 'Trakt (Trending, Popular, etc.)' },
  { value: 'tmdb', label: 'TMDb (Popular, Top Rated, etc.)' },
  { value: 'tautulli', label: 'Tautulli (Most Watched)' },
  { value: 'genre', label: 'Genre Collections' },
  { value: 'franchise', label: 'Franchise Collections' },
  { value: 'universe', label: 'Universe Collections (MCU, etc.)' },
  { value: 'decade', label: 'Decade Collections' },
  { value: 'year', label: 'Year Collections' },
  { value: 'content_rating_us', label: 'Content Rating (US)' },
  { value: 'content_rating_uk', label: 'Content Rating (UK)' },
  { value: 'resolution', label: 'Resolution Collections' },
  { value: 'audio_language', label: 'Audio Language Collections' },
  { value: 'subtitle_language', label: 'Subtitle Language Collections' },
  { value: 'streaming', label: 'Streaming Services' },
  { value: 'studio', label: 'Studio Collections' },
  { value: 'network', label: 'Network Collections' },
  { value: 'country', label: 'Country Collections' },
  { value: 'region', label: 'Region Collections' },
  { value: 'aspect', label: 'Aspect Ratio Collections' },
  { value: 'based', label: 'Based On (Books, Comics, etc.)' },
  { value: 'actor', label: 'Actor Collections' },
  { value: 'director', label: 'Director Collections' },
  { value: 'producer', label: 'Producer Collections' },
  { value: 'writer', label: 'Writer Collections' },
  { value: 'seasonal', label: 'Seasonal Collections' },
  { value: 'award', label: 'Award Collections' },
  { value: 'chart', label: 'Chart Collections' },
  { value: 'collectionless', label: 'Collectionless' },
  { value: 'separator', label: 'Separators' },
];

const defaultOverlayOptions = [
  { value: '', label: 'Custom file path...' },
  { value: 'resolution', label: 'Resolution Overlay (4K, 1080p, etc.)' },
  { value: 'audio_codec', label: 'Audio Codec Overlay' },
  { value: 'video_format', label: 'Video Format Overlay' },
  { value: 'streaming', label: 'Streaming Service Overlay' },
  { value: 'ratings', label: 'Ratings Overlay' },
  { value: 'status', label: 'Status Overlay (Continuing, Ended)' },
  { value: 'ribbon', label: 'Ribbon Overlays' },
  { value: 'runtimes', label: 'Runtime Overlay' },
  { value: 'languages', label: 'Language Flags Overlay' },
  { value: 'mediastinger', label: 'Media Stinger Overlay' },
  { value: 'commonsense', label: 'Common Sense Age Rating' },
  { value: 'direct_play', label: 'Direct Play Overlay' },
];

const scheduleOptions = [
  { value: '', label: 'No schedule (always run)' },
  { value: 'hourly', label: 'Hourly' },
  { value: 'daily', label: 'Daily' },
  { value: 'weekly', label: 'Weekly' },
  { value: 'monthly', label: 'Monthly' },
  { value: 'yearly', label: 'Yearly' },
  { value: 'range(01/01-12/31)', label: 'Date Range' },
  { value: 'never', label: 'Never (disabled)' },
];

const massUpdateOptions = [
  { value: '', label: 'No update' },
  { value: 'tmdb', label: 'TMDb' },
  { value: 'imdb', label: 'IMDb' },
  { value: 'trakt_user', label: 'Trakt User' },
  { value: 'omdb', label: 'OMDb' },
  { value: 'mdb', label: 'MDBList' },
  { value: 'mdb_average', label: 'MDBList Average' },
  { value: 'anidb', label: 'AniDB' },
  { value: 'mal', label: 'MyAnimeList' },
  { value: 'lock', label: 'Lock current value' },
  { value: 'unlock', label: 'Unlock current value' },
  { value: 'remove', label: 'Remove value' },
  { value: 'reset', label: 'Reset to default' },
];

function getActiveTab(name: string) {
  return activeTab.value[name] || 'collections';
}

function setActiveTab(name: string, tab: string) {
  activeTab.value = { ...activeTab.value, [name]: tab };
}

function addLibrary() {
  if (!newLibraryName.value.trim()) return;

  emit('update:modelValue', {
    ...props.modelValue,
    [newLibraryName.value]: {
      collection_files: [],
      overlay_files: [],
    },
  });
  newLibraryName.value = '';
  showAddModal.value = false;
}

function removeLibrary(name: string) {
  const updated = { ...props.modelValue };
  delete updated[name];
  emit('update:modelValue', updated);
}

function updateLibrary(name: string, config: LibraryConfig) {
  emit('update:modelValue', {
    ...props.modelValue,
    [name]: config,
  });
}

function addFileToLibrary(
  libraryName: string,
  fileType: 'collection_files' | 'overlay_files' | 'metadata_files',
  fileValue: string,
  isDefault: boolean = false
) {
  const library = props.modelValue[libraryName];
  if (!library || !fileValue.trim()) return;

  const files = library[fileType] || [];
  const newEntry: string | CollectionFile = isDefault
    ? { default: fileValue }
    : { file: fileValue };

  updateLibrary(libraryName, {
    ...library,
    [fileType]: [...files, newEntry],
  });

  // Clear the input
  if (fileType === 'collection_files') {
    newCollectionFile.value[libraryName] = '';
  } else if (fileType === 'overlay_files') {
    newOverlayFile.value[libraryName] = '';
  } else {
    newMetadataFile.value[libraryName] = '';
  }
}

function removeFileFromLibrary(
  libraryName: string,
  fileType: 'collection_files' | 'overlay_files' | 'metadata_files',
  index: number
) {
  const library = props.modelValue[libraryName];
  if (!library) return;

  const files = [...(library[fileType] || [])];
  files.splice(index, 1);
  updateLibrary(libraryName, {
    ...library,
    [fileType]: files,
  });
}

function getFileDisplay(file: string | CollectionFile): string {
  if (typeof file === 'string') return file;
  if (file.default) return `Default: ${file.default}`;
  if (file.file) return file.file;
  return 'Unknown';
}

function getFileType(file: string | CollectionFile): 'default' | 'file' {
  if (typeof file === 'string') return 'file';
  return file.default ? 'default' : 'file';
}

function updateOperations(libraryName: string, operations: LibraryOperations) {
  const library = props.modelValue[libraryName];
  if (!library) return;

  updateLibrary(libraryName, {
    ...library,
    operations,
  });
}

function getOperations(libraryName: string): LibraryOperations {
  return props.modelValue[libraryName]?.operations || {};
}
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-start justify-between">
      <div>
        <div class="flex items-center gap-2">
          <span class="text-2xl">📚</span>
          <h3 class="text-lg font-semibold">Libraries</h3>
          <span class="text-xs px-2 py-0.5 rounded bg-error/20 text-error font-medium">Required</span>
        </div>
        <p class="mt-1 text-sm text-content-secondary">
          Configure which Plex libraries Kometa should manage. Each library can have its own collection, overlay, and metadata files.
        </p>
      </div>
      <a
        href="https://kometa.wiki/en/latest/config/libraries/"
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

    <!-- Library List -->
    <div v-if="libraries.length > 0" class="space-y-4">
      <Card
        v-for="[name, config] in libraries"
        :key="name"
        class="overflow-hidden"
        padding="none"
      >
        <!-- Library Header -->
        <div class="flex items-center justify-between p-4 bg-surface-secondary border-b border-border">
          <div class="flex items-center gap-3">
            <span class="text-xl">📁</span>
            <span class="font-semibold text-lg">{{ name }}</span>
            <Badge v-if="config.schedule && config.schedule !== 'never'" variant="default" size="sm">
              {{ config.schedule }}
            </Badge>
            <Badge v-if="config.schedule === 'never'" variant="warning" size="sm">
              Disabled
            </Badge>
          </div>
          <div class="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              @click="editingLibrary = editingLibrary === name ? null : name"
            >
              {{ editingLibrary === name ? 'Collapse' : 'Expand' }}
            </Button>
            <Button
              variant="ghost"
              size="sm"
              class="text-error hover:bg-error/10"
              @click="removeLibrary(name)"
            >
              Remove
            </Button>
          </div>
        </div>

        <!-- Summary view (collapsed) -->
        <div v-if="editingLibrary !== name" class="p-4">
          <div class="flex flex-wrap gap-4 text-sm">
            <div class="flex items-center gap-2">
              <span class="text-content-muted">Collections:</span>
              <Badge variant="default" size="sm">{{ (config.collection_files || []).length }} files</Badge>
            </div>
            <div class="flex items-center gap-2">
              <span class="text-content-muted">Overlays:</span>
              <Badge variant="default" size="sm">{{ (config.overlay_files || []).length }} files</Badge>
            </div>
            <div class="flex items-center gap-2">
              <span class="text-content-muted">Metadata:</span>
              <Badge variant="default" size="sm">{{ (config.metadata_files || []).length }} files</Badge>
            </div>
            <div v-if="config.operations && Object.keys(config.operations).length > 0" class="flex items-center gap-2">
              <span class="text-content-muted">Operations:</span>
              <Badge variant="success" size="sm">Configured</Badge>
            </div>
          </div>
        </div>

        <!-- Expanded Edit View -->
        <div v-else class="p-4">
          <!-- Tabs -->
          <div class="flex border-b border-border mb-4">
            <button
              v-for="tab in ['collections', 'overlays', 'metadata', 'operations', 'settings']"
              :key="tab"
              class="px-4 py-2 text-sm font-medium border-b-2 -mb-px transition-colors"
              :class="getActiveTab(name) === tab
                ? 'border-kometa-gold text-kometa-gold'
                : 'border-transparent text-content-muted hover:text-content'"
              @click="setActiveTab(name, tab)"
            >
              {{ tab.charAt(0).toUpperCase() + tab.slice(1) }}
            </button>
          </div>

          <!-- Collections Tab -->
          <div v-if="getActiveTab(name) === 'collections'" class="space-y-4">
            <p class="text-sm text-content-secondary">
              Add collection files to build and manage Plex collections. Use default files from Kometa or specify custom file paths.
            </p>

            <!-- Existing Files -->
            <div v-if="(config.collection_files || []).length > 0" class="space-y-2">
              <div
                v-for="(file, idx) in config.collection_files"
                :key="idx"
                class="flex items-center gap-2 p-3 rounded-lg bg-surface-tertiary"
              >
                <Badge
                  :variant="getFileType(file) === 'default' ? 'success' : 'default'"
                  size="sm"
                >
                  {{ getFileType(file) === 'default' ? 'Default' : 'File' }}
                </Badge>
                <span class="flex-1 font-mono text-sm">{{ getFileDisplay(file) }}</span>
                <button
                  class="p-1.5 rounded hover:bg-error/20 text-content-muted hover:text-error transition-colors"
                  title="Remove file"
                  @click="removeFileFromLibrary(name, 'collection_files', idx)"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            <!-- Add New File -->
            <div class="p-4 rounded-lg bg-surface-secondary border border-border">
              <h5 class="font-medium mb-3">Add Collection File</h5>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium mb-2">Default Collection</label>
                  <Select
                    :model-value="''"
                    :options="defaultCollectionOptions"
                    placeholder="Select a default collection..."
                    @update:model-value="(val: string) => val && addFileToLibrary(name, 'collection_files', val, true)"
                  />
                  <p class="text-xs text-content-muted mt-1">Pre-built collection files from Kometa</p>
                </div>
                <div>
                  <label class="block text-sm font-medium mb-2">Custom File Path</label>
                  <div class="flex gap-2">
                    <Input
                      v-model="newCollectionFile[name]"
                      placeholder="config/MyCollections.yml"
                      class="flex-1"
                      @keydown.enter="addFileToLibrary(name, 'collection_files', newCollectionFile[name] || '')"
                    />
                    <Button
                      variant="secondary"
                      size="sm"
                      :disabled="!newCollectionFile[name]"
                      @click="addFileToLibrary(name, 'collection_files', newCollectionFile[name] || '')"
                    >
                      Add
                    </Button>
                  </div>
                  <p class="text-xs text-content-muted mt-1">Path to your custom collection file</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Overlays Tab -->
          <div v-if="getActiveTab(name) === 'overlays'" class="space-y-4">
            <p class="text-sm text-content-secondary">
              Add overlay files to apply visual overlays (resolution badges, ratings, etc.) to your library items.
            </p>

            <!-- Existing Files -->
            <div v-if="(config.overlay_files || []).length > 0" class="space-y-2">
              <div
                v-for="(file, idx) in config.overlay_files"
                :key="idx"
                class="flex items-center gap-2 p-3 rounded-lg bg-surface-tertiary"
              >
                <Badge
                  :variant="getFileType(file) === 'default' ? 'success' : 'default'"
                  size="sm"
                >
                  {{ getFileType(file) === 'default' ? 'Default' : 'File' }}
                </Badge>
                <span class="flex-1 font-mono text-sm">{{ getFileDisplay(file) }}</span>
                <button
                  class="p-1.5 rounded hover:bg-error/20 text-content-muted hover:text-error transition-colors"
                  title="Remove file"
                  @click="removeFileFromLibrary(name, 'overlay_files', idx)"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            <!-- Add New File -->
            <div class="p-4 rounded-lg bg-surface-secondary border border-border">
              <h5 class="font-medium mb-3">Add Overlay File</h5>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium mb-2">Default Overlay</label>
                  <Select
                    :model-value="''"
                    :options="defaultOverlayOptions"
                    placeholder="Select a default overlay..."
                    @update:model-value="(val: string) => val && addFileToLibrary(name, 'overlay_files', val, true)"
                  />
                  <p class="text-xs text-content-muted mt-1">Pre-built overlay files from Kometa</p>
                </div>
                <div>
                  <label class="block text-sm font-medium mb-2">Custom File Path</label>
                  <div class="flex gap-2">
                    <Input
                      v-model="newOverlayFile[name]"
                      placeholder="config/MyOverlays.yml"
                      class="flex-1"
                      @keydown.enter="addFileToLibrary(name, 'overlay_files', newOverlayFile[name] || '')"
                    />
                    <Button
                      variant="secondary"
                      size="sm"
                      :disabled="!newOverlayFile[name]"
                      @click="addFileToLibrary(name, 'overlay_files', newOverlayFile[name] || '')"
                    >
                      Add
                    </Button>
                  </div>
                  <p class="text-xs text-content-muted mt-1">Path to your custom overlay file</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Metadata Tab -->
          <div v-if="getActiveTab(name) === 'metadata'" class="space-y-4">
            <p class="text-sm text-content-secondary">
              Add metadata files to update item metadata (titles, descriptions, posters, etc.) in your library.
            </p>

            <!-- Existing Files -->
            <div v-if="(config.metadata_files || []).length > 0" class="space-y-2">
              <div
                v-for="(file, idx) in config.metadata_files"
                :key="idx"
                class="flex items-center gap-2 p-3 rounded-lg bg-surface-tertiary"
              >
                <Badge variant="default" size="sm">File</Badge>
                <span class="flex-1 font-mono text-sm">{{ getFileDisplay(file) }}</span>
                <button
                  class="p-1.5 rounded hover:bg-error/20 text-content-muted hover:text-error transition-colors"
                  title="Remove file"
                  @click="removeFileFromLibrary(name, 'metadata_files', idx)"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            <!-- Add New File -->
            <div class="p-4 rounded-lg bg-surface-secondary border border-border">
              <h5 class="font-medium mb-3">Add Metadata File</h5>
              <div class="flex gap-2">
                <Input
                  v-model="newMetadataFile[name]"
                  placeholder="config/MyMetadata.yml"
                  class="flex-1"
                  @keydown.enter="addFileToLibrary(name, 'metadata_files', newMetadataFile[name] || '')"
                />
                <Button
                  variant="secondary"
                  size="sm"
                  :disabled="!newMetadataFile[name]"
                  @click="addFileToLibrary(name, 'metadata_files', newMetadataFile[name] || '')"
                >
                  Add
                </Button>
              </div>
            </div>
          </div>

          <!-- Operations Tab -->
          <div v-if="getActiveTab(name) === 'operations'" class="space-y-6">
            <p class="text-sm text-content-secondary">
              Configure library-wide operations to mass update metadata, manage duplicates, and sync with Radarr/Sonarr.
            </p>

            <!-- Mass Update Operations -->
            <div class="p-4 rounded-lg bg-surface-secondary border border-border">
              <h5 class="font-medium mb-4 flex items-center gap-2">
                <span>📊</span> Mass Update Operations
              </h5>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <FormField label="Mass Genre Update" tooltip="Update genres for all items from a source">
                  <Select
                    :model-value="getOperations(name).mass_genre_update || ''"
                    :options="massUpdateOptions"
                    @update:model-value="updateOperations(name, { ...getOperations(name), mass_genre_update: $event || undefined })"
                  />
                </FormField>

                <FormField label="Mass Audience Rating" tooltip="Update audience ratings from a source">
                  <Select
                    :model-value="getOperations(name).mass_audience_rating_update || ''"
                    :options="massUpdateOptions"
                    @update:model-value="updateOperations(name, { ...getOperations(name), mass_audience_rating_update: $event || undefined })"
                  />
                </FormField>

                <FormField label="Mass Critic Rating" tooltip="Update critic ratings from a source">
                  <Select
                    :model-value="getOperations(name).mass_critic_rating_update || ''"
                    :options="massUpdateOptions"
                    @update:model-value="updateOperations(name, { ...getOperations(name), mass_critic_rating_update: $event || undefined })"
                  />
                </FormField>

                <FormField label="Mass Content Rating" tooltip="Update content ratings from a source">
                  <Select
                    :model-value="getOperations(name).mass_content_rating_update || ''"
                    :options="massUpdateOptions"
                    @update:model-value="updateOperations(name, { ...getOperations(name), mass_content_rating_update: $event || undefined })"
                  />
                </FormField>
              </div>
            </div>

            <!-- Radarr/Sonarr Integration -->
            <div class="p-4 rounded-lg bg-surface-secondary border border-border">
              <h5 class="font-medium mb-4 flex items-center gap-2">
                <span>🎬</span> Radarr / Sonarr Integration
              </h5>
              <div class="space-y-3">
                <Checkbox
                  :model-value="getOperations(name).radarr_add_all || false"
                  @update:model-value="updateOperations(name, { ...getOperations(name), radarr_add_all: $event })"
                >
                  <span class="font-medium">Radarr Add All</span>
                  <span class="text-content-secondary ml-2">Add all movies from this library to Radarr</span>
                </Checkbox>

                <Checkbox
                  :model-value="getOperations(name).sonarr_add_all || false"
                  @update:model-value="updateOperations(name, { ...getOperations(name), sonarr_add_all: $event })"
                >
                  <span class="font-medium">Sonarr Add All</span>
                  <span class="text-content-secondary ml-2">Add all shows from this library to Sonarr</span>
                </Checkbox>

                <FormField label="Radarr Remove By Tag" tooltip="Remove movies from Radarr that have this tag">
                  <Input
                    :model-value="getOperations(name).radarr_remove_by_tag || ''"
                    placeholder="tag_name"
                    @update:model-value="updateOperations(name, { ...getOperations(name), radarr_remove_by_tag: $event || undefined })"
                  />
                </FormField>

                <FormField label="Sonarr Remove By Tag" tooltip="Remove shows from Sonarr that have this tag">
                  <Input
                    :model-value="getOperations(name).sonarr_remove_by_tag || ''"
                    placeholder="tag_name"
                    @update:model-value="updateOperations(name, { ...getOperations(name), sonarr_remove_by_tag: $event || undefined })"
                  />
                </FormField>
              </div>
            </div>

            <!-- Other Operations -->
            <div class="p-4 rounded-lg bg-surface-secondary border border-border">
              <h5 class="font-medium mb-4 flex items-center gap-2">
                <span>🔧</span> Other Operations
              </h5>
              <div class="space-y-3">
                <Checkbox
                  :model-value="getOperations(name).split_duplicates || false"
                  @update:model-value="updateOperations(name, { ...getOperations(name), split_duplicates: $event })"
                >
                  <span class="font-medium">Split Duplicates</span>
                  <span class="text-content-secondary ml-2">Split items with multiple editions into separate entries</span>
                </Checkbox>

                <Checkbox
                  :model-value="getOperations(name).assets_for_all || false"
                  @update:model-value="updateOperations(name, { ...getOperations(name), assets_for_all: $event })"
                >
                  <span class="font-medium">Assets for All</span>
                  <span class="text-content-secondary ml-2">Search for and apply assets to all library items</span>
                </Checkbox>
              </div>
            </div>
          </div>

          <!-- Settings Tab -->
          <div v-if="getActiveTab(name) === 'settings'" class="space-y-6">
            <p class="text-sm text-content-secondary">
              Configure library-specific settings including schedule, report path, and other options.
            </p>

            <!-- Schedule -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FormField
                label="Schedule"
                tooltip="When this library should be processed"
                help="Controls when Kometa processes this library"
              >
                <Select
                  :model-value="config.schedule || ''"
                  :options="scheduleOptions"
                  @update:model-value="updateLibrary(name, { ...config, schedule: $event || undefined })"
                />
              </FormField>

              <FormField
                label="Custom Schedule"
                tooltip="Enter a custom cron expression or schedule"
                help="e.g., daily, weekly(monday), range(01/01-03/31)"
              >
                <Input
                  :model-value="config.schedule || ''"
                  placeholder="daily"
                  @update:model-value="updateLibrary(name, { ...config, schedule: $event || undefined })"
                />
              </FormField>
            </div>

            <!-- Report & Asset Paths -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FormField
                label="Report Path"
                tooltip="Path to save library reports"
                help="Leave empty to use default"
              >
                <Input
                  :model-value="config.report_path || ''"
                  placeholder="config/reports/movies"
                  @update:model-value="updateLibrary(name, { ...config, report_path: $event || undefined })"
                />
              </FormField>

              <FormField
                label="Asset Directory"
                tooltip="Custom asset directory for this library"
                help="Override global asset directory"
              >
                <Input
                  :model-value="config.asset_directory || ''"
                  placeholder="config/assets/movies"
                  @update:model-value="updateLibrary(name, { ...config, asset_directory: $event || undefined })"
                />
              </FormField>
            </div>

            <!-- Collection Management -->
            <div class="p-4 rounded-lg bg-surface-secondary border border-border">
              <h5 class="font-medium mb-4">Collection Management</h5>
              <div class="space-y-3">
                <Checkbox
                  :model-value="config.delete_unmanaged_collections || false"
                  @update:model-value="updateLibrary(name, { ...config, delete_unmanaged_collections: $event })"
                >
                  <span class="font-medium">Delete Unmanaged Collections</span>
                  <span class="text-content-secondary ml-2">Remove collections not managed by Kometa</span>
                </Checkbox>

                <FormField
                  label="Delete Collections With Less Than"
                  tooltip="Delete collections with fewer items than this number"
                  help="Set to 0 to disable"
                >
                  <Input
                    type="number"
                    :model-value="String(config.delete_collections_with_less || 0)"
                    min="0"
                    @update:model-value="updateLibrary(name, { ...config, delete_collections_with_less: Number($event) || undefined })"
                  />
                </FormField>
              </div>
            </div>
          </div>
        </div>
      </Card>
    </div>

    <!-- Empty State -->
    <div
      v-else
      class="text-center py-12 border-2 border-dashed border-border rounded-lg"
    >
      <span class="text-4xl mb-4 block">📚</span>
      <h4 class="text-lg font-medium mb-2">No Libraries Configured</h4>
      <p class="text-content-secondary mb-4">Add a Plex library to start building collections and overlays</p>
      <Button @click="showAddModal = true">
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Add Library
      </Button>
    </div>

    <!-- Add Library Button -->
    <Button
      v-if="libraries.length > 0"
      variant="secondary"
      class="w-full"
      @click="showAddModal = true"
    >
      <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
      </svg>
      Add Another Library
    </Button>

    <!-- Add Library Modal -->
    <Modal
      v-model:open="showAddModal"
      title="Add Library"
      size="sm"
    >
      <div class="space-y-4">
        <FormField
          label="Library Name"
          required
          help="Enter the exact name of your Plex library (case-sensitive)"
        >
          <Input
            v-model="newLibraryName"
            placeholder="Movies"
            @keydown.enter="addLibrary"
          />
        </FormField>

        <div class="p-3 rounded-lg bg-surface-tertiary text-sm">
          <p class="font-medium mb-1">Common Library Names:</p>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="suggestion in ['Movies', 'TV Shows', 'Anime', '4K Movies', '4K TV Shows', 'Kids Movies', 'Documentaries']"
              :key="suggestion"
              class="px-2 py-1 rounded bg-surface-secondary hover:bg-kometa-gold/20 text-content-secondary hover:text-kometa-gold transition-colors"
              @click="newLibraryName = suggestion"
            >
              {{ suggestion }}
            </button>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="flex justify-end gap-2">
          <Button variant="secondary" @click="showAddModal = false">
            Cancel
          </Button>
          <Button :disabled="!newLibraryName.trim()" @click="addLibrary">
            Add Library
          </Button>
        </div>
      </template>
    </Modal>
  </div>
</template>
