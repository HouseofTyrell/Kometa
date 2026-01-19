<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { stringify, parse } from 'yaml';
import { Card, Button, Badge, Modal, Input, Select, Checkbox } from '@/components/common';
import { YamlHighlight } from '@/components/common';
import FormField from '@/components/config/FormField.vue';
import { useToast } from '@/composables';

const toast = useToast();

// File management state
const files = ref<CollectionFileData[]>([]);
const activeFileIndex = ref<number | null>(null);
const showNewFileModal = ref(false);
const showAddCollectionModal = ref(false);
const showAddOverlayModal = ref(false);
const viewMode = ref<'gui' | 'yaml' | 'split'>('split');

// New file form
const newFileName = ref('');
const newFileType = ref<'collection' | 'overlay'>('collection');

// New collection form
const newCollectionName = ref('');
const newCollectionBuilder = ref('tmdb_list');
const newCollectionBuilderValue = ref('');

// New overlay form
const newOverlayName = ref('');
const newOverlayType = ref<'resolution' | 'rating' | 'custom'>('resolution');

interface CollectionFileData {
  name: string;
  type: 'collection' | 'overlay';
  content: CollectionFileContent;
  isDirty: boolean;
}

interface CollectionFileContent {
  collections?: Record<string, CollectionDefinition>;
  dynamic_collections?: Record<string, DynamicCollectionDefinition>;
  overlays?: Record<string, OverlayDefinition>;
  templates?: Record<string, unknown>;
}

interface CollectionDefinition {
  [key: string]: unknown;
  // Builders
  tmdb_list?: string | string[];
  tmdb_collection?: string | number;
  tmdb_discover?: Record<string, unknown>;
  imdb_list?: string | string[];
  imdb_chart?: string;
  trakt_list?: string | string[];
  plex_search?: Record<string, unknown>;
  plex_all?: boolean;
  mdblist_list?: string | string[];
  // Settings
  sync_mode?: 'sync' | 'append';
  collection_order?: string;
  sort_title?: string;
  summary?: string;
  url_poster?: string;
  schedule?: string;
  // Filters
  filters?: Record<string, unknown>;
  // Radarr/Sonarr
  radarr_add_missing?: boolean;
  sonarr_add_missing?: boolean;
}

interface DynamicCollectionDefinition {
  type: string;
  data?: Record<string, unknown>;
  title_format?: string;
  template?: unknown[];
  template_variables?: Record<string, unknown>;
}

interface OverlayDefinition {
  overlay?: OverlaySettings;
  plex_search?: Record<string, unknown>;
  plex_all?: boolean;
  weight?: number;
  group?: string;
  builder_level?: 'show' | 'season' | 'episode';
}

interface OverlaySettings {
  name: string;
  horizontal_align?: 'left' | 'center' | 'right';
  horizontal_offset?: number;
  vertical_align?: 'top' | 'center' | 'bottom';
  vertical_offset?: number;
  font_color?: string;
  font_size?: number;
  back_color?: string;
  back_width?: number;
  back_height?: number;
  back_radius?: number;
}

const activeFile = computed(() =>
  activeFileIndex.value !== null ? files.value[activeFileIndex.value] : null
);

const yamlContent = computed(() => {
  if (!activeFile.value) return '';
  try {
    return stringify(activeFile.value.content, { lineWidth: 0 });
  } catch {
    return '# Error generating YAML';
  }
});

const collectionsList = computed(() => {
  if (!activeFile.value?.content.collections) return [];
  return Object.entries(activeFile.value.content.collections);
});

const overlaysList = computed(() => {
  if (!activeFile.value?.content.overlays) return [];
  return Object.entries(activeFile.value.content.overlays);
});

// Builder options
const builderOptions = [
  { value: 'tmdb_list', label: 'TMDb List' },
  { value: 'tmdb_collection', label: 'TMDb Collection' },
  { value: 'tmdb_discover', label: 'TMDb Discover' },
  { value: 'tmdb_popular', label: 'TMDb Popular' },
  { value: 'tmdb_trending_daily', label: 'TMDb Trending Daily' },
  { value: 'tmdb_trending_weekly', label: 'TMDb Trending Weekly' },
  { value: 'imdb_list', label: 'IMDb List' },
  { value: 'imdb_chart', label: 'IMDb Chart' },
  { value: 'trakt_list', label: 'Trakt List' },
  { value: 'trakt_trending', label: 'Trakt Trending' },
  { value: 'trakt_popular', label: 'Trakt Popular' },
  { value: 'mdblist_list', label: 'MDBList' },
  { value: 'plex_search', label: 'Plex Search' },
  { value: 'plex_all', label: 'Plex All Items' },
  { value: 'tautulli_popular', label: 'Tautulli Popular' },
  { value: 'letterboxd_list', label: 'Letterboxd List' },
];

const imdbChartOptions = [
  { value: 'top_movies', label: 'Top 250 Movies' },
  { value: 'top_english', label: 'Top English Movies' },
  { value: 'top_indian', label: 'Top Indian Movies' },
  { value: 'popular_movies', label: 'Most Popular Movies' },
  { value: 'lowest_rated', label: 'Lowest Rated Movies' },
  { value: 'top_250_tvs', label: 'Top 250 TV Shows' },
  { value: 'popular_tvs', label: 'Most Popular TV Shows' },
];

const overlayTypeOptions = [
  { value: 'resolution', label: 'Resolution (4K, 1080p, etc.)' },
  { value: 'rating', label: 'Rating Overlay' },
  { value: 'audio', label: 'Audio Codec' },
  { value: 'streaming', label: 'Streaming Service' },
  { value: 'custom', label: 'Custom Image/Text' },
];

function createNewFile() {
  if (!newFileName.value.trim()) return;

  const fileName = newFileName.value.endsWith('.yml')
    ? newFileName.value
    : `${newFileName.value}.yml`;

  const newFile: CollectionFileData = {
    name: fileName,
    type: newFileType.value,
    content: newFileType.value === 'collection'
      ? { collections: {} }
      : { overlays: {} },
    isDirty: true,
  };

  files.value.push(newFile);
  activeFileIndex.value = files.value.length - 1;
  showNewFileModal.value = false;
  newFileName.value = '';
  toast.success(`Created ${fileName}`);
}

function addCollection() {
  if (!activeFile.value || !newCollectionName.value.trim()) return;

  const collection: CollectionDefinition = {};

  // Add the builder
  if (newCollectionBuilder.value === 'plex_all') {
    collection.plex_all = true;
  } else if (newCollectionBuilder.value === 'imdb_chart') {
    collection.imdb_chart = newCollectionBuilderValue.value || 'top_movies';
  } else if (newCollectionBuilderValue.value) {
    collection[newCollectionBuilder.value] = newCollectionBuilderValue.value;
  }

  // Default settings
  collection.sync_mode = 'sync';
  collection.collection_order = 'release';

  if (!activeFile.value.content.collections) {
    activeFile.value.content.collections = {};
  }

  activeFile.value.content.collections[newCollectionName.value] = collection;
  activeFile.value.isDirty = true;

  showAddCollectionModal.value = false;
  newCollectionName.value = '';
  newCollectionBuilderValue.value = '';
  toast.success(`Added collection: ${newCollectionName.value}`);
}

function removeCollection(name: string) {
  if (!activeFile.value?.content.collections) return;
  delete activeFile.value.content.collections[name];
  activeFile.value.isDirty = true;
}

function addOverlay() {
  if (!activeFile.value || !newOverlayName.value.trim()) return;

  const overlay: OverlayDefinition = {
    overlay: {
      name: newOverlayType.value === 'custom'
        ? 'custom_overlay.png'
        : `text(<<${newOverlayType.value}>>)`,
      horizontal_align: 'left',
      horizontal_offset: 15,
      vertical_align: 'top',
      vertical_offset: 15,
    },
    plex_all: true,
  };

  if (!activeFile.value.content.overlays) {
    activeFile.value.content.overlays = {};
  }

  activeFile.value.content.overlays[newOverlayName.value] = overlay;
  activeFile.value.isDirty = true;

  showAddOverlayModal.value = false;
  newOverlayName.value = '';
  toast.success(`Added overlay: ${newOverlayName.value}`);
}

function removeOverlay(name: string) {
  if (!activeFile.value?.content.overlays) return;
  delete activeFile.value.content.overlays[name];
  activeFile.value.isDirty = true;
}

function updateCollectionField(collectionName: string, field: string, value: unknown) {
  if (!activeFile.value?.content.collections?.[collectionName]) return;
  if (value === '' || value === undefined) {
    delete activeFile.value.content.collections[collectionName][field];
  } else {
    activeFile.value.content.collections[collectionName][field] = value;
  }
  activeFile.value.isDirty = true;
}

function updateOverlayField(overlayName: string, field: string, value: unknown) {
  if (!activeFile.value?.content.overlays?.[overlayName]) return;
  if (field.startsWith('overlay.')) {
    const subField = field.replace('overlay.', '');
    if (!activeFile.value.content.overlays[overlayName].overlay) {
      activeFile.value.content.overlays[overlayName].overlay = { name: '' };
    }
    (activeFile.value.content.overlays[overlayName].overlay as Record<string, unknown>)[subField] = value;
  } else {
    (activeFile.value.content.overlays[overlayName] as Record<string, unknown>)[field] = value;
  }
  activeFile.value.isDirty = true;
}

function downloadFile() {
  if (!activeFile.value) return;

  const blob = new Blob([yamlContent.value], { type: 'text/yaml' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = activeFile.value.name;
  a.click();
  URL.revokeObjectURL(url);

  activeFile.value.isDirty = false;
  toast.success(`Downloaded ${activeFile.value.name}`);
}

function closeFile(index: number) {
  files.value.splice(index, 1);
  if (activeFileIndex.value === index) {
    activeFileIndex.value = files.value.length > 0 ? 0 : null;
  } else if (activeFileIndex.value !== null && activeFileIndex.value > index) {
    activeFileIndex.value--;
  }
}

function handleYamlEdit(content: string) {
  if (!activeFile.value) return;
  try {
    activeFile.value.content = parse(content) || {};
    activeFile.value.isDirty = true;
  } catch (err) {
    // Invalid YAML, don't update
  }
}
</script>

<template>
  <div class="h-full flex flex-col">
    <!-- Header -->
    <div class="px-6 py-4 border-b border-border bg-surface-secondary">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-semibold text-content">Collection & Overlay Editor</h1>
          <p class="text-sm text-content-secondary mt-1">
            Create and edit collection and overlay definition files
          </p>
        </div>
        <div class="flex items-center gap-2">
          <Button variant="secondary" @click="showNewFileModal = true">
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            New File
          </Button>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="flex-1 flex min-h-0">
      <!-- File List Sidebar -->
      <div class="w-64 border-r border-border bg-surface-primary flex flex-col">
        <div class="p-3 border-b border-border">
          <h3 class="text-sm font-medium text-content-secondary uppercase tracking-wider">Files</h3>
        </div>

        <div v-if="files.length === 0" class="flex-1 flex items-center justify-center p-4">
          <div class="text-center text-content-muted">
            <svg class="w-12 h-12 mx-auto mb-3 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p class="text-sm">No files yet</p>
            <p class="text-xs mt-1">Create a new file to get started</p>
          </div>
        </div>

        <div v-else class="flex-1 overflow-auto">
          <div
            v-for="(file, index) in files"
            :key="index"
            class="flex items-center gap-2 px-3 py-2 cursor-pointer border-b border-border/50 transition-colors"
            :class="activeFileIndex === index ? 'bg-kometa-gold/10 text-kometa-gold' : 'hover:bg-surface-tertiary'"
            @click="activeFileIndex = index"
          >
            <svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <span class="flex-1 truncate text-sm font-medium">{{ file.name }}</span>
            <Badge v-if="file.isDirty" variant="warning" size="sm">*</Badge>
            <Badge :variant="file.type === 'collection' ? 'default' : 'success'" size="sm">
              {{ file.type === 'collection' ? 'C' : 'O' }}
            </Badge>
            <button
              class="p-1 rounded hover:bg-error/20 text-content-muted hover:text-error"
              @click.stop="closeFile(index)"
            >
              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      <!-- Editor Area -->
      <div v-if="activeFile" class="flex-1 flex flex-col min-h-0">
        <!-- Editor Toolbar -->
        <div class="flex items-center justify-between px-4 py-2 border-b border-border bg-surface-secondary">
          <div class="flex items-center gap-2">
            <span class="font-medium">{{ activeFile.name }}</span>
            <Badge v-if="activeFile.isDirty" variant="warning">Unsaved</Badge>
          </div>
          <div class="flex items-center gap-2">
            <!-- View Mode Toggle -->
            <div class="flex rounded-lg border border-border overflow-hidden">
              <button
                v-for="mode in ['gui', 'split', 'yaml']"
                :key="mode"
                class="px-3 py-1 text-xs font-medium transition-colors"
                :class="viewMode === mode ? 'bg-kometa-gold text-black' : 'bg-surface-primary text-content-secondary hover:bg-surface-tertiary'"
                @click="viewMode = mode as 'gui' | 'yaml' | 'split'"
              >
                {{ mode.toUpperCase() }}
              </button>
            </div>

            <!-- Add Buttons -->
            <Button
              v-if="activeFile.type === 'collection'"
              variant="secondary"
              size="sm"
              @click="showAddCollectionModal = true"
            >
              + Collection
            </Button>
            <Button
              v-else
              variant="secondary"
              size="sm"
              @click="showAddOverlayModal = true"
            >
              + Overlay
            </Button>

            <Button variant="primary" size="sm" @click="downloadFile">
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              Download
            </Button>
          </div>
        </div>

        <!-- Editor Content -->
        <div class="flex-1 flex min-h-0">
          <!-- GUI Panel -->
          <div
            v-if="viewMode !== 'yaml'"
            class="flex-1 overflow-auto p-4"
            :class="{ 'border-r border-border': viewMode === 'split' }"
          >
            <!-- Collections List -->
            <div v-if="activeFile.type === 'collection'" class="space-y-4">
              <div v-if="collectionsList.length === 0" class="text-center py-12 text-content-muted">
                <span class="text-4xl mb-4 block">📚</span>
                <p>No collections yet</p>
                <Button variant="secondary" size="sm" class="mt-4" @click="showAddCollectionModal = true">
                  Add your first collection
                </Button>
              </div>

              <Card
                v-for="[name, collection] in collectionsList"
                :key="name"
                padding="none"
              >
                <div class="p-4 border-b border-border bg-surface-secondary flex items-center justify-between">
                  <div class="flex items-center gap-3">
                    <span class="text-xl">📚</span>
                    <span class="font-semibold">{{ name }}</span>
                  </div>
                  <button
                    class="p-1.5 rounded hover:bg-error/20 text-content-muted hover:text-error"
                    @click="removeCollection(name)"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>

                <div class="p-4 space-y-4">
                  <!-- Builder Info -->
                  <div class="grid grid-cols-2 gap-4">
                    <FormField label="Builder">
                      <Select
                        :model-value="Object.keys(collection).find(k => builderOptions.some(b => b.value === k)) || ''"
                        :options="builderOptions"
                        @update:model-value="(v: string) => {
                          // Remove old builder and add new one
                          const oldBuilder = Object.keys(collection).find(k => builderOptions.some(b => b.value === k));
                          if (oldBuilder) updateCollectionField(name, oldBuilder, undefined);
                          updateCollectionField(name, v, '');
                        }"
                      />
                    </FormField>

                    <FormField label="Builder Value">
                      <Input
                        :model-value="String(collection[Object.keys(collection).find(k => builderOptions.some(b => b.value === k)) || ''] || '')"
                        placeholder="List ID or URL"
                        @update:model-value="(v: string) => {
                          const builder = Object.keys(collection).find(k => builderOptions.some(b => b.value === k));
                          if (builder) updateCollectionField(name, builder, v);
                        }"
                      />
                    </FormField>
                  </div>

                  <!-- Settings -->
                  <div class="grid grid-cols-2 gap-4">
                    <FormField label="Sync Mode">
                      <Select
                        :model-value="(collection as CollectionDefinition).sync_mode || 'sync'"
                        :options="[
                          { value: 'sync', label: 'Sync (replace items)' },
                          { value: 'append', label: 'Append (add items)' },
                        ]"
                        @update:model-value="(v: string) => updateCollectionField(name, 'sync_mode', v)"
                      />
                    </FormField>

                    <FormField label="Collection Order">
                      <Select
                        :model-value="(collection as CollectionDefinition).collection_order || ''"
                        :options="[
                          { value: '', label: 'Default' },
                          { value: 'release', label: 'Release Date' },
                          { value: 'alpha', label: 'Alphabetical' },
                          { value: 'custom', label: 'Custom' },
                          { value: 'random', label: 'Random' },
                        ]"
                        @update:model-value="(v: string) => updateCollectionField(name, 'collection_order', v || undefined)"
                      />
                    </FormField>
                  </div>

                  <div class="grid grid-cols-2 gap-4">
                    <FormField label="Sort Title" tooltip="Controls position in collection list">
                      <Input
                        :model-value="(collection as CollectionDefinition).sort_title || ''"
                        placeholder="e.g., !01_Popular"
                        @update:model-value="(v: string) => updateCollectionField(name, 'sort_title', v || undefined)"
                      />
                    </FormField>

                    <FormField label="Schedule">
                      <Input
                        :model-value="(collection as CollectionDefinition).schedule || ''"
                        placeholder="e.g., daily, weekly(monday)"
                        @update:model-value="(v: string) => updateCollectionField(name, 'schedule', v || undefined)"
                      />
                    </FormField>
                  </div>

                  <FormField label="Summary">
                    <Input
                      :model-value="(collection as CollectionDefinition).summary || ''"
                      placeholder="Collection description"
                      @update:model-value="(v: string) => updateCollectionField(name, 'summary', v || undefined)"
                    />
                  </FormField>

                  <FormField label="Poster URL">
                    <Input
                      :model-value="(collection as CollectionDefinition).url_poster || ''"
                      placeholder="https://..."
                      @update:model-value="(v: string) => updateCollectionField(name, 'url_poster', v || undefined)"
                    />
                  </FormField>

                  <!-- Arr Integration -->
                  <div class="flex items-center gap-6 pt-2">
                    <Checkbox
                      :model-value="(collection as CollectionDefinition).radarr_add_missing || false"
                      @update:model-value="(v: boolean) => updateCollectionField(name, 'radarr_add_missing', v || undefined)"
                    >
                      Add missing to Radarr
                    </Checkbox>
                    <Checkbox
                      :model-value="(collection as CollectionDefinition).sonarr_add_missing || false"
                      @update:model-value="(v: boolean) => updateCollectionField(name, 'sonarr_add_missing', v || undefined)"
                    >
                      Add missing to Sonarr
                    </Checkbox>
                  </div>
                </div>
              </Card>
            </div>

            <!-- Overlays List -->
            <div v-else class="space-y-4">
              <div v-if="overlaysList.length === 0" class="text-center py-12 text-content-muted">
                <span class="text-4xl mb-4 block">🎨</span>
                <p>No overlays yet</p>
                <Button variant="secondary" size="sm" class="mt-4" @click="showAddOverlayModal = true">
                  Add your first overlay
                </Button>
              </div>

              <Card
                v-for="[name, overlay] in overlaysList"
                :key="name"
                padding="none"
              >
                <div class="p-4 border-b border-border bg-surface-secondary flex items-center justify-between">
                  <div class="flex items-center gap-3">
                    <span class="text-xl">🎨</span>
                    <span class="font-semibold">{{ name }}</span>
                  </div>
                  <button
                    class="p-1.5 rounded hover:bg-error/20 text-content-muted hover:text-error"
                    @click="removeOverlay(name)"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>

                <div class="p-4 space-y-4">
                  <!-- Overlay Settings -->
                  <FormField label="Overlay Name/Image">
                    <Input
                      :model-value="(overlay as OverlayDefinition).overlay?.name || ''"
                      placeholder="image.png or text(<<text>>)"
                      @update:model-value="(v: string) => updateOverlayField(name, 'overlay.name', v)"
                    />
                  </FormField>

                  <div class="grid grid-cols-4 gap-4">
                    <FormField label="H. Align">
                      <Select
                        :model-value="(overlay as OverlayDefinition).overlay?.horizontal_align || 'left'"
                        :options="[
                          { value: 'left', label: 'Left' },
                          { value: 'center', label: 'Center' },
                          { value: 'right', label: 'Right' },
                        ]"
                        @update:model-value="(v: string) => updateOverlayField(name, 'overlay.horizontal_align', v)"
                      />
                    </FormField>

                    <FormField label="H. Offset">
                      <Input
                        type="number"
                        :model-value="String((overlay as OverlayDefinition).overlay?.horizontal_offset || 15)"
                        @update:model-value="(v: string) => updateOverlayField(name, 'overlay.horizontal_offset', Number(v))"
                      />
                    </FormField>

                    <FormField label="V. Align">
                      <Select
                        :model-value="(overlay as OverlayDefinition).overlay?.vertical_align || 'top'"
                        :options="[
                          { value: 'top', label: 'Top' },
                          { value: 'center', label: 'Center' },
                          { value: 'bottom', label: 'Bottom' },
                        ]"
                        @update:model-value="(v: string) => updateOverlayField(name, 'overlay.vertical_align', v)"
                      />
                    </FormField>

                    <FormField label="V. Offset">
                      <Input
                        type="number"
                        :model-value="String((overlay as OverlayDefinition).overlay?.vertical_offset || 15)"
                        @update:model-value="(v: string) => updateOverlayField(name, 'overlay.vertical_offset', Number(v))"
                      />
                    </FormField>
                  </div>

                  <div class="grid grid-cols-3 gap-4">
                    <FormField label="Weight (Priority)">
                      <Input
                        type="number"
                        :model-value="String((overlay as OverlayDefinition).weight || '')"
                        placeholder="10"
                        @update:model-value="(v: string) => updateOverlayField(name, 'weight', v ? Number(v) : undefined)"
                      />
                    </FormField>

                    <FormField label="Group">
                      <Input
                        :model-value="(overlay as OverlayDefinition).group || ''"
                        placeholder="resolution"
                        @update:model-value="(v: string) => updateOverlayField(name, 'group', v || undefined)"
                      />
                    </FormField>

                    <FormField label="Builder Level">
                      <Select
                        :model-value="(overlay as OverlayDefinition).builder_level || ''"
                        :options="[
                          { value: '', label: 'Default' },
                          { value: 'show', label: 'Show' },
                          { value: 'season', label: 'Season' },
                          { value: 'episode', label: 'Episode' },
                        ]"
                        @update:model-value="(v: string) => updateOverlayField(name, 'builder_level', v || undefined)"
                      />
                    </FormField>
                  </div>
                </div>
              </Card>
            </div>
          </div>

          <!-- YAML Panel -->
          <div
            v-if="viewMode !== 'gui'"
            class="flex-1 flex flex-col min-h-0"
            :class="{ 'max-w-[50%]': viewMode === 'split' }"
          >
            <Card class="flex-1 flex flex-col min-h-0" padding="none">
              <template #header>
                <span class="font-medium font-mono text-sm">{{ activeFile.name }}</span>
              </template>
              <div class="flex-1 min-h-0 overflow-auto p-4 bg-surface-primary">
                <YamlHighlight :content="yamlContent" />
              </div>
            </Card>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="flex-1 flex items-center justify-center bg-surface-primary">
        <div class="text-center">
          <span class="text-6xl mb-4 block">📚</span>
          <h2 class="text-xl font-semibold mb-2">Collection & Overlay Editor</h2>
          <p class="text-content-secondary mb-6 max-w-md">
            Create collection and overlay files that define how Kometa builds your Plex collections and applies overlays.
          </p>
          <Button @click="showNewFileModal = true">
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            Create New File
          </Button>
        </div>
      </div>
    </div>

    <!-- New File Modal -->
    <Modal
      v-model:open="showNewFileModal"
      title="Create New File"
      size="sm"
    >
      <div class="space-y-4">
        <FormField label="File Name" required>
          <Input
            v-model="newFileName"
            placeholder="my_collections.yml"
            @keydown.enter="createNewFile"
          />
        </FormField>

        <FormField label="File Type">
          <div class="flex gap-4">
            <label class="flex items-center gap-2 cursor-pointer">
              <input
                type="radio"
                v-model="newFileType"
                value="collection"
                class="text-kometa-gold focus:ring-kometa-gold"
              />
              <span>Collection File</span>
            </label>
            <label class="flex items-center gap-2 cursor-pointer">
              <input
                type="radio"
                v-model="newFileType"
                value="overlay"
                class="text-kometa-gold focus:ring-kometa-gold"
              />
              <span>Overlay File</span>
            </label>
          </div>
        </FormField>
      </div>

      <template #footer>
        <div class="flex justify-end gap-2">
          <Button variant="secondary" @click="showNewFileModal = false">Cancel</Button>
          <Button :disabled="!newFileName.trim()" @click="createNewFile">Create</Button>
        </div>
      </template>
    </Modal>

    <!-- Add Collection Modal -->
    <Modal
      v-model:open="showAddCollectionModal"
      title="Add Collection"
      size="md"
    >
      <div class="space-y-4">
        <FormField label="Collection Name" required>
          <Input
            v-model="newCollectionName"
            placeholder="My Awesome Collection"
          />
        </FormField>

        <FormField label="Builder Type">
          <Select
            v-model="newCollectionBuilder"
            :options="builderOptions"
          />
        </FormField>

        <FormField
          v-if="newCollectionBuilder === 'imdb_chart'"
          label="IMDb Chart"
        >
          <Select
            v-model="newCollectionBuilderValue"
            :options="imdbChartOptions"
          />
        </FormField>

        <FormField
          v-else-if="newCollectionBuilder !== 'plex_all'"
          label="Builder Value"
          :help="newCollectionBuilder.includes('list') ? 'Enter the list ID or URL' : 'Enter the value for this builder'"
        >
          <Input
            v-model="newCollectionBuilderValue"
            :placeholder="newCollectionBuilder.includes('list') ? 'List ID or URL' : 'Value'"
          />
        </FormField>
      </div>

      <template #footer>
        <div class="flex justify-end gap-2">
          <Button variant="secondary" @click="showAddCollectionModal = false">Cancel</Button>
          <Button :disabled="!newCollectionName.trim()" @click="addCollection">Add Collection</Button>
        </div>
      </template>
    </Modal>

    <!-- Add Overlay Modal -->
    <Modal
      v-model:open="showAddOverlayModal"
      title="Add Overlay"
      size="sm"
    >
      <div class="space-y-4">
        <FormField label="Overlay Name" required>
          <Input
            v-model="newOverlayName"
            placeholder="4K Resolution"
          />
        </FormField>

        <FormField label="Overlay Type">
          <Select
            v-model="newOverlayType"
            :options="overlayTypeOptions"
          />
        </FormField>
      </div>

      <template #footer>
        <div class="flex justify-end gap-2">
          <Button variant="secondary" @click="showAddOverlayModal = false">Cancel</Button>
          <Button :disabled="!newOverlayName.trim()" @click="addOverlay">Add Overlay</Button>
        </div>
      </template>
    </Modal>
  </div>
</template>
