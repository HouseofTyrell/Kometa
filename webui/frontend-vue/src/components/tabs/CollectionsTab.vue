<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
import { stringify, parse } from 'yaml';
import { Card, Button, Badge, Modal, Input, Select, Checkbox } from '@/components/common';
import { YamlHighlight } from '@/components/common';
import FormField from '@/components/config/FormField.vue';
import { useToast } from '@/composables';

const toast = useToast();

// Unsaved changes warning
const hasUnsavedChanges = computed(() => files.value.some(f => f.isDirty));

function handleBeforeUnload(e: BeforeUnloadEvent) {
  if (hasUnsavedChanges.value) {
    e.preventDefault();
    e.returnValue = 'You have unsaved changes. Are you sure you want to leave?';
    return e.returnValue;
  }
}

onMounted(() => {
  window.addEventListener('beforeunload', handleBeforeUnload);
});

onUnmounted(() => {
  window.removeEventListener('beforeunload', handleBeforeUnload);
});

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
  tmdb_collection_details?: string | number;
  tmdb_movie?: string | number | (string | number)[];
  tmdb_show?: string | number | (string | number)[];
  tmdb_discover?: Record<string, unknown>;
  tmdb_popular?: number;
  tmdb_trending_daily?: number;
  tmdb_trending_weekly?: number;
  tmdb_top_rated?: number;
  tmdb_now_playing?: number;
  tmdb_upcoming?: number;
  imdb_list?: string | string[];
  imdb_chart?: string;
  imdb_search?: Record<string, unknown>;
  trakt_list?: string | string[];
  trakt_list_details?: string | string[];
  trakt_chart?: string;
  trakt_userlist?: string | string[];
  trakt_recommendations?: number;
  trakt_trending?: number;
  trakt_popular?: number;
  trakt_watched?: number;
  trakt_collected?: number;
  plex_search?: Record<string, unknown>;
  plex_all?: boolean;
  mdblist_list?: string | string[];
  letterboxd_list?: string | string[];
  letterboxd_list_details?: string | string[];
  icheckmovies_list?: string | string[];
  stevenlu_popular?: boolean;
  anidb_id?: number | number[];
  anidb_relation?: number | number[];
  anidb_popular?: number;
  anidb_tag?: string | string[];
  mal_id?: number | number[];
  mal_search?: Record<string, unknown>;
  mal_userlist?: Record<string, unknown>;
  mal_season?: Record<string, unknown>;
  mal_suggested?: number;
  mal_popular?: number;
  mal_favorite?: number;
  mal_top_rated?: number;
  mal_top_airing?: number;
  mal_top_upcoming?: number;
  mal_top_tv?: number;
  mal_top_movie?: number;
  reciperr_list?: string | string[];
  tautulli_popular?: number;
  tautulli_watched?: number;
  // Settings
  sync_mode?: 'sync' | 'append';
  collection_order?: string;
  custom_sort?: Record<string, number>;
  sort_title?: string;
  name_mapping?: string;
  label?: string | string[];
  label_sync_mode?: 'sync' | 'append';
  summary?: string;
  url_poster?: string;
  url_background?: string;
  url_theme?: string;
  file_poster?: string;
  file_background?: string;
  tmdb_poster?: number;
  tmdb_background?: number;
  tmdb_profile?: number;
  tvdb_poster?: number;
  tvdb_background?: number;
  visible_library?: boolean;
  visible_home?: boolean;
  visible_shared?: boolean;
  collection_mode?: 'default' | 'hide' | 'hide_items' | 'show_items';
  collection_filtering?: 'user' | 'admin';
  minimum_items?: number;
  delete_below_minimum?: boolean;
  delete_not_scheduled?: boolean;
  schedule?: string;
  run_again_delay?: number;
  missing_only_released?: boolean;
  only_filter_missing?: boolean;
  // Smart Filters
  smart_label?: string;
  smart_url?: string;
  smart_filter?: Record<string, unknown>;
  // Filters
  filters?: Record<string, unknown>;
  plex_collectionless?: Record<string, unknown>;
  // Radarr/Sonarr
  radarr_add_missing?: boolean;
  radarr_add_existing?: boolean;
  radarr_folder?: string;
  radarr_monitor?: boolean;
  radarr_availability?: string;
  radarr_quality?: string;
  radarr_tag?: string | string[];
  radarr_search?: boolean;
  sonarr_add_missing?: boolean;
  sonarr_add_existing?: boolean;
  sonarr_folder?: string;
  sonarr_monitor?: string;
  sonarr_quality?: string;
  sonarr_language?: string;
  sonarr_series?: string;
  sonarr_season?: boolean;
  sonarr_tag?: string | string[];
  sonarr_search?: boolean;
  // Item Details
  item_label?: string | string[];
  item_radarr_tag?: string | string[];
  item_sonarr_tag?: string | string[];
  item_overlay?: string;
  item_lock_poster?: boolean;
  item_lock_background?: boolean;
  item_lock_title?: boolean;
  item_refresh?: boolean;
  item_refresh_delay?: number;
  item_tmdb_season_titles?: boolean;
  item_episode_sorting?: string;
  item_keep_episodes?: string;
  item_delete_episodes?: string;
  item_season_display?: string;
  item_episode_ordering?: string;
  item_metadata_language?: string;
  item_use_original_title?: string;
  // Other
  cache_builders?: number;
  blank_collection?: boolean;
  build_collection?: boolean;
  server_preroll?: string;
  changes_webhooks?: string | string[];
}

interface DynamicCollectionDefinition {
  type: string;
  data?: Record<string, unknown>;
  title_format?: string;
  template?: unknown[];
  template_variables?: Record<string, unknown>;
}

interface OverlayDefinition {
  [key: string]: unknown;
  overlay?: OverlaySettings;
  // Builders (same as collections)
  plex_search?: Record<string, unknown>;
  plex_all?: boolean;
  tmdb_discover?: Record<string, unknown>;
  tmdb_list?: string | string[];
  imdb_list?: string | string[];
  trakt_list?: string | string[];
  mdblist_list?: string | string[];
  // Overlay-specific
  weight?: number;
  group?: string;
  queue?: string;
  queues?: Record<string, string[]>;
  builder_level?: 'show' | 'season' | 'episode';
  suppress_overlays?: string | string[];
  // Filters
  filters?: Record<string, unknown>;
  // Schedule
  schedule?: string;
}

interface OverlaySettings {
  name: string;
  // File/URL options
  file?: string;
  url?: string;
  git?: string;
  repo?: string;
  // Position
  horizontal_align?: 'left' | 'center' | 'right';
  horizontal_offset?: number;
  vertical_align?: 'top' | 'center' | 'bottom';
  vertical_offset?: number;
  // Font settings
  font?: string;
  font_style?: string;
  font_size?: number;
  font_color?: string;
  stroke_color?: string;
  stroke_width?: number;
  // Background settings
  back_color?: string;
  back_width?: number;
  back_height?: number;
  back_radius?: number;
  back_line_color?: string;
  back_line_width?: number;
  back_padding?: number;
  back_align?: 'left' | 'center' | 'right';
  // Special text options
  addon_offset?: number;
  addon_position?: 'left' | 'right' | 'top' | 'bottom';
  // PMM special overlays
  pmm?: string;
  // Coordinates
  x_coordinate?: number;
  y_coordinate?: number;
  x_align?: 'left' | 'center' | 'right';
  y_align?: 'top' | 'center' | 'bottom';
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

// Builder options with descriptions
const builderOptions = [
  { value: 'tmdb_list', label: 'TMDb List', description: 'Build from a TMDb list by ID or URL. Great for curated lists like "Best Sci-Fi Movies".' },
  { value: 'tmdb_collection', label: 'TMDb Collection', description: 'Build from TMDb movie collections (franchises like Marvel, Star Wars, etc.).' },
  { value: 'tmdb_discover', label: 'TMDb Discover', description: 'Use TMDb\'s discover API with filters for genre, year, rating, etc.' },
  { value: 'tmdb_popular', label: 'TMDb Popular', description: 'Current most popular movies/shows on TMDb. Updates automatically.' },
  { value: 'tmdb_trending_daily', label: 'TMDb Trending Daily', description: 'What\'s trending today on TMDb. Refreshes daily.' },
  { value: 'tmdb_trending_weekly', label: 'TMDb Trending Weekly', description: 'What\'s trending this week on TMDb. Refreshes weekly.' },
  { value: 'imdb_list', label: 'IMDb List', description: 'Build from an IMDb list URL. Works with any public IMDb list.' },
  { value: 'imdb_chart', label: 'IMDb Chart', description: 'Use official IMDb charts like Top 250, Most Popular, etc.' },
  { value: 'trakt_list', label: 'Trakt List', description: 'Build from a Trakt list URL. Great for community-curated lists.' },
  { value: 'trakt_trending', label: 'Trakt Trending', description: 'Currently trending on Trakt based on user activity.' },
  { value: 'trakt_popular', label: 'Trakt Popular', description: 'Most popular all-time on Trakt based on user ratings.' },
  { value: 'mdblist_list', label: 'MDBList', description: 'Build from MDBList lists. Supports complex filtering across multiple sources.' },
  { value: 'plex_search', label: 'Plex Search', description: 'Search your Plex library with filters (genre, year, rating, etc.).' },
  { value: 'plex_all', label: 'Plex All Items', description: 'Include all items in your Plex library. Useful with filters.' },
  { value: 'tautulli_popular', label: 'Tautulli Popular', description: 'Most watched in your Plex server based on Tautulli stats.' },
  { value: 'letterboxd_list', label: 'Letterboxd List', description: 'Build from Letterboxd lists. Great for film enthusiast collections.' },
];

// Get description for selected builder
const selectedBuilderDescription = computed(() => {
  const builder = builderOptions.find(b => b.value === newCollectionBuilder.value);
  return builder?.description || '';
});

const imdbChartOptions = [
  { value: 'top_movies', label: 'Top 250 Movies', description: 'IMDb\'s highest-rated 250 movies of all time' },
  { value: 'top_english', label: 'Top English Movies', description: 'Highest-rated English language movies' },
  { value: 'top_indian', label: 'Top Indian Movies', description: 'Highest-rated Indian movies' },
  { value: 'popular_movies', label: 'Most Popular Movies', description: 'Currently most popular movies on IMDb' },
  { value: 'lowest_rated', label: 'Lowest Rated Movies', description: 'The infamous bottom 100 movies' },
  { value: 'top_250_tvs', label: 'Top 250 TV Shows', description: 'IMDb\'s highest-rated 250 TV shows' },
  { value: 'popular_tvs', label: 'Most Popular TV Shows', description: 'Currently most popular TV shows on IMDb' },
];

const overlayTypeOptions = [
  { value: 'resolution', label: 'Resolution', description: 'Shows video resolution (4K, 1080p, 720p, etc.) on posters' },
  { value: 'rating', label: 'Rating', description: 'Displays IMDb, TMDb, or other ratings on posters' },
  { value: 'audio', label: 'Audio Codec', description: 'Shows audio format (Dolby Atmos, DTS-X, etc.)' },
  { value: 'streaming', label: 'Streaming Service', description: 'Shows which streaming service has the content' },
  { value: 'custom', label: 'Custom Image/Text', description: 'Use your own image or text overlay' },
];

// Get description for selected overlay type
const selectedOverlayDescription = computed(() => {
  const overlay = overlayTypeOptions.find(o => o.value === newOverlayType.value);
  return overlay?.description || '';
});

// Schedule options
const scheduleOptions = [
  { value: '', label: 'No Schedule (Always Run)' },
  { value: 'hourly', label: 'Hourly' },
  { value: 'daily', label: 'Daily' },
  { value: 'weekly', label: 'Weekly' },
  { value: 'weekly(monday)', label: 'Weekly (Monday)' },
  { value: 'weekly(friday)', label: 'Weekly (Friday)' },
  { value: 'weekly(sunday)', label: 'Weekly (Sunday)' },
  { value: 'monthly', label: 'Monthly' },
  { value: 'monthly(1)', label: 'Monthly (1st)' },
  { value: 'monthly(15)', label: 'Monthly (15th)' },
  { value: 'yearly', label: 'Yearly' },
  { value: 'range(01/01-03/31)', label: 'Q1 (Jan-Mar)' },
  { value: 'range(04/01-06/30)', label: 'Q2 (Apr-Jun)' },
  { value: 'range(07/01-09/30)', label: 'Q3 (Jul-Sep)' },
  { value: 'range(10/01-12/31)', label: 'Q4 (Oct-Dec)' },
  { value: 'never', label: 'Never (Disabled)' },
];

// Collection order options
const collectionOrderOptions = [
  { value: '', label: 'Default (Library Default)', description: 'Use the library\'s default sort order' },
  { value: 'release', label: 'Release Date', description: 'Sort by original release date' },
  { value: 'release.desc', label: 'Release Date (Newest First)', description: 'Newest releases first' },
  { value: 'release.asc', label: 'Release Date (Oldest First)', description: 'Oldest releases first' },
  { value: 'alpha', label: 'Alphabetical', description: 'Sort alphabetically by title' },
  { value: 'alpha.desc', label: 'Alphabetical (Z-A)', description: 'Reverse alphabetical order' },
  { value: 'custom', label: 'Custom', description: 'Keep the order from the source list/builder' },
  { value: 'random', label: 'Random', description: 'Randomize order on each run' },
  { value: 'critic_rating.desc', label: 'Critic Rating (High-Low)', description: 'Highest critic ratings first' },
  { value: 'audience_rating.desc', label: 'Audience Rating (High-Low)', description: 'Highest audience ratings first' },
  { value: 'user_rating.desc', label: 'User Rating (High-Low)', description: 'Highest user ratings first' },
  { value: 'duration.desc', label: 'Duration (Longest First)', description: 'Longest runtime first' },
  { value: 'duration.asc', label: 'Duration (Shortest First)', description: 'Shortest runtime first' },
  { value: 'added.desc', label: 'Recently Added', description: 'Most recently added to library' },
  { value: 'added.asc', label: 'First Added', description: 'Oldest additions to library' },
];

// Collection mode options
const collectionModeOptions = [
  { value: 'default', label: 'Default', description: 'Use Plex default behavior' },
  { value: 'hide', label: 'Hide Collection', description: 'Hide the collection but keep items visible' },
  { value: 'hide_items', label: 'Hide Items', description: 'Hide items when in this collection' },
  { value: 'show_items', label: 'Show Items', description: 'Always show items regardless of settings' },
];

// Visibility options
const visibilityOptions = [
  { value: '', label: 'Default' },
  { value: 'true', label: 'Visible' },
  { value: 'false', label: 'Hidden' },
];

// Radarr availability options
const radarrAvailabilityOptions = [
  { value: 'announced', label: 'Announced', description: 'Movie has been announced' },
  { value: 'in_cinemas', label: 'In Cinemas', description: 'Movie is playing in theaters' },
  { value: 'released', label: 'Released', description: 'Movie is physically/digitally released' },
];

// Sonarr monitor options
const sonarrMonitorOptions = [
  { value: 'all', label: 'All Episodes', description: 'Monitor all episodes' },
  { value: 'future', label: 'Future Episodes', description: 'Only monitor unaired episodes' },
  { value: 'missing', label: 'Missing Episodes', description: 'Only monitor episodes not on disk' },
  { value: 'existing', label: 'Existing Episodes', description: 'Only monitor episodes on disk' },
  { value: 'pilot', label: 'Pilot Only', description: 'Only monitor the pilot episode' },
  { value: 'first', label: 'First Season', description: 'Only monitor the first season' },
  { value: 'latest', label: 'Latest Season', description: 'Only monitor the latest season' },
  { value: 'none', label: 'None', description: 'Don\'t monitor any episodes' },
];

// Collection state for expanded sections
const expandedCollectionSections = ref<Record<string, Set<string>>>({});

function toggleCollectionSection(collectionName: string, section: string) {
  if (!expandedCollectionSections.value[collectionName]) {
    expandedCollectionSections.value[collectionName] = new Set(['builder', 'basic']);
  }
  const sections = expandedCollectionSections.value[collectionName];
  if (sections.has(section)) {
    sections.delete(section);
  } else {
    sections.add(section);
  }
}

function isCollectionSectionExpanded(collectionName: string, section: string): boolean {
  if (!expandedCollectionSections.value[collectionName]) {
    expandedCollectionSections.value[collectionName] = new Set(['builder', 'basic']);
  }
  return expandedCollectionSections.value[collectionName].has(section);
}

// Overlay state for expanded sections
const expandedOverlaySections = ref<Record<string, Set<string>>>({});

function toggleOverlaySection(overlayName: string, section: string) {
  if (!expandedOverlaySections.value[overlayName]) {
    expandedOverlaySections.value[overlayName] = new Set(['basic', 'position']);
  }
  const sections = expandedOverlaySections.value[overlayName];
  if (sections.has(section)) {
    sections.delete(section);
  } else {
    sections.add(section);
  }
}

function isOverlaySectionExpanded(overlayName: string, section: string): boolean {
  if (!expandedOverlaySections.value[overlayName]) {
    expandedOverlaySections.value[overlayName] = new Set(['basic', 'position']);
  }
  return expandedOverlaySections.value[overlayName].has(section);
}

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

                <div class="divide-y divide-border">
                  <!-- Builder Section -->
                  <div class="p-4">
                    <button
                      class="w-full flex items-center justify-between text-left"
                      @click="toggleCollectionSection(name, 'builder')"
                    >
                      <span class="font-medium flex items-center gap-2">
                        <span>🔧</span> Builder
                      </span>
                      <svg
                        class="w-5 h-5 transition-transform"
                        :class="{ 'rotate-180': isCollectionSectionExpanded(name, 'builder') }"
                        fill="none" stroke="currentColor" viewBox="0 0 24 24"
                      >
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                      </svg>
                    </button>
                    <div v-if="isCollectionSectionExpanded(name, 'builder')" class="mt-4 space-y-4">
                      <div class="grid grid-cols-2 gap-4">
                        <FormField label="Builder Type" tooltip="The source for building this collection">
                          <Select
                            :model-value="Object.keys(collection).find(k => builderOptions.some(b => b.value === k)) || ''"
                            :options="builderOptions"
                            @update:model-value="(v: string) => {
                              const oldBuilder = Object.keys(collection).find(k => builderOptions.some(b => b.value === k));
                              if (oldBuilder) updateCollectionField(name, oldBuilder, undefined);
                              updateCollectionField(name, v, '');
                            }"
                          />
                        </FormField>
                        <FormField label="Builder Value" tooltip="The ID, URL, or value for the builder">
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
                      <div class="grid grid-cols-2 gap-4">
                        <FormField label="Limit" tooltip="Maximum number of items to add">
                          <Input
                            type="number"
                            :model-value="String((collection as CollectionDefinition).limit || '')"
                            placeholder="No limit"
                            @update:model-value="(v: string) => updateCollectionField(name, 'limit', v ? Number(v) : undefined)"
                          />
                        </FormField>
                        <FormField label="Cache Builders" tooltip="Days to cache builder results">
                          <Input
                            type="number"
                            :model-value="String((collection as CollectionDefinition).cache_builders || '')"
                            placeholder="Default"
                            @update:model-value="(v: string) => updateCollectionField(name, 'cache_builders', v ? Number(v) : undefined)"
                          />
                        </FormField>
                      </div>
                    </div>
                  </div>

                  <!-- Basic Settings Section -->
                  <div class="p-4">
                    <button
                      class="w-full flex items-center justify-between text-left"
                      @click="toggleCollectionSection(name, 'basic')"
                    >
                      <span class="font-medium flex items-center gap-2">
                        <span>⚙️</span> Basic Settings
                      </span>
                      <svg
                        class="w-5 h-5 transition-transform"
                        :class="{ 'rotate-180': isCollectionSectionExpanded(name, 'basic') }"
                        fill="none" stroke="currentColor" viewBox="0 0 24 24"
                      >
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                      </svg>
                    </button>
                    <div v-if="isCollectionSectionExpanded(name, 'basic')" class="mt-4 space-y-4">
                      <div class="grid grid-cols-2 gap-4">
                        <FormField label="Sync Mode" tooltip="How to handle existing items">
                          <Select
                            :model-value="(collection as CollectionDefinition).sync_mode || 'sync'"
                            :options="[
                              { value: 'sync', label: 'Sync (replace items)' },
                              { value: 'append', label: 'Append (add items)' },
                            ]"
                            @update:model-value="(v: string) => updateCollectionField(name, 'sync_mode', v)"
                          />
                        </FormField>
                        <FormField label="Collection Order" tooltip="Sort order for items in collection">
                          <Select
                            :model-value="(collection as CollectionDefinition).collection_order || ''"
                            :options="collectionOrderOptions"
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
                        <FormField label="Name Mapping" tooltip="Name used for asset lookups">
                          <Input
                            :model-value="(collection as CollectionDefinition).name_mapping || ''"
                            placeholder="Same as collection name"
                            @update:model-value="(v: string) => updateCollectionField(name, 'name_mapping', v || undefined)"
                          />
                        </FormField>
                      </div>
                      <div class="grid grid-cols-2 gap-4">
                        <FormField label="Schedule" tooltip="When to run this collection">
                          <Select
                            :model-value="(collection as CollectionDefinition).schedule || ''"
                            :options="scheduleOptions"
                            @update:model-value="(v: string) => updateCollectionField(name, 'schedule', v || undefined)"
                          />
                        </FormField>
                        <FormField label="Collection Mode" tooltip="How the collection appears in Plex">
                          <Select
                            :model-value="(collection as CollectionDefinition).collection_mode || 'default'"
                            :options="collectionModeOptions"
                            @update:model-value="(v: string) => updateCollectionField(name, 'collection_mode', v || undefined)"
                          />
                        </FormField>
                      </div>
                      <FormField label="Summary" tooltip="Collection description shown in Plex">
                        <Input
                          :model-value="(collection as CollectionDefinition).summary || ''"
                          placeholder="Collection description"
                          @update:model-value="(v: string) => updateCollectionField(name, 'summary', v || undefined)"
                        />
                      </FormField>
                      <FormField label="Labels" tooltip="Plex labels to apply to this collection">
                        <Input
                          :model-value="Array.isArray((collection as CollectionDefinition).label) ? (collection as CollectionDefinition).label?.join(', ') : ((collection as CollectionDefinition).label || '')"
                          placeholder="label1, label2"
                          @update:model-value="(v: string) => updateCollectionField(name, 'label', v ? v.split(',').map(s => s.trim()) : undefined)"
                        />
                      </FormField>
                    </div>
                  </div>

                  <!-- Artwork Section -->
                  <div class="p-4">
                    <button
                      class="w-full flex items-center justify-between text-left"
                      @click="toggleCollectionSection(name, 'artwork')"
                    >
                      <span class="font-medium flex items-center gap-2">
                        <span>🖼️</span> Artwork
                      </span>
                      <svg
                        class="w-5 h-5 transition-transform"
                        :class="{ 'rotate-180': isCollectionSectionExpanded(name, 'artwork') }"
                        fill="none" stroke="currentColor" viewBox="0 0 24 24"
                      >
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                      </svg>
                    </button>
                    <div v-if="isCollectionSectionExpanded(name, 'artwork')" class="mt-4 space-y-4">
                      <div class="grid grid-cols-2 gap-4">
                        <FormField label="Poster URL" tooltip="URL for collection poster">
                          <Input
                            :model-value="(collection as CollectionDefinition).url_poster || ''"
                            placeholder="https://..."
                            @update:model-value="(v: string) => updateCollectionField(name, 'url_poster', v || undefined)"
                          />
                        </FormField>
                        <FormField label="Background URL" tooltip="URL for collection background">
                          <Input
                            :model-value="(collection as CollectionDefinition).url_background || ''"
                            placeholder="https://..."
                            @update:model-value="(v: string) => updateCollectionField(name, 'url_background', v || undefined)"
                          />
                        </FormField>
                      </div>
                      <div class="grid grid-cols-2 gap-4">
                        <FormField label="File Poster" tooltip="Local file path for poster">
                          <Input
                            :model-value="(collection as CollectionDefinition).file_poster || ''"
                            placeholder="config/posters/collection.png"
                            @update:model-value="(v: string) => updateCollectionField(name, 'file_poster', v || undefined)"
                          />
                        </FormField>
                        <FormField label="File Background" tooltip="Local file path for background">
                          <Input
                            :model-value="(collection as CollectionDefinition).file_background || ''"
                            placeholder="config/backgrounds/collection.png"
                            @update:model-value="(v: string) => updateCollectionField(name, 'file_background', v || undefined)"
                          />
                        </FormField>
                      </div>
                      <div class="grid grid-cols-3 gap-4">
                        <FormField label="TMDb Poster ID" tooltip="TMDb movie/show ID for poster">
                          <Input
                            type="number"
                            :model-value="String((collection as CollectionDefinition).tmdb_poster || '')"
                            placeholder="TMDb ID"
                            @update:model-value="(v: string) => updateCollectionField(name, 'tmdb_poster', v ? Number(v) : undefined)"
                          />
                        </FormField>
                        <FormField label="TMDb Background ID" tooltip="TMDb movie/show ID for background">
                          <Input
                            type="number"
                            :model-value="String((collection as CollectionDefinition).tmdb_background || '')"
                            placeholder="TMDb ID"
                            @update:model-value="(v: string) => updateCollectionField(name, 'tmdb_background', v ? Number(v) : undefined)"
                          />
                        </FormField>
                        <FormField label="TMDb Profile ID" tooltip="TMDb person ID for poster">
                          <Input
                            type="number"
                            :model-value="String((collection as CollectionDefinition).tmdb_profile || '')"
                            placeholder="TMDb Person ID"
                            @update:model-value="(v: string) => updateCollectionField(name, 'tmdb_profile', v ? Number(v) : undefined)"
                          />
                        </FormField>
                      </div>
                    </div>
                  </div>

                  <!-- Visibility Section -->
                  <div class="p-4">
                    <button
                      class="w-full flex items-center justify-between text-left"
                      @click="toggleCollectionSection(name, 'visibility')"
                    >
                      <span class="font-medium flex items-center gap-2">
                        <span>👁️</span> Visibility
                      </span>
                      <svg
                        class="w-5 h-5 transition-transform"
                        :class="{ 'rotate-180': isCollectionSectionExpanded(name, 'visibility') }"
                        fill="none" stroke="currentColor" viewBox="0 0 24 24"
                      >
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                      </svg>
                    </button>
                    <div v-if="isCollectionSectionExpanded(name, 'visibility')" class="mt-4 space-y-4">
                      <div class="grid grid-cols-3 gap-4">
                        <Checkbox
                          :model-value="(collection as CollectionDefinition).visible_library ?? true"
                          @update:model-value="(v: boolean) => updateCollectionField(name, 'visible_library', v)"
                        >
                          Visible in Library
                        </Checkbox>
                        <Checkbox
                          :model-value="(collection as CollectionDefinition).visible_home ?? false"
                          @update:model-value="(v: boolean) => updateCollectionField(name, 'visible_home', v || undefined)"
                        >
                          Visible on Home
                        </Checkbox>
                        <Checkbox
                          :model-value="(collection as CollectionDefinition).visible_shared ?? false"
                          @update:model-value="(v: boolean) => updateCollectionField(name, 'visible_shared', v || undefined)"
                        >
                          Visible to Shared Users
                        </Checkbox>
                      </div>
                      <div class="grid grid-cols-2 gap-4">
                        <FormField label="Minimum Items" tooltip="Minimum items to show collection">
                          <Input
                            type="number"
                            :model-value="String((collection as CollectionDefinition).minimum_items || '')"
                            placeholder="1"
                            @update:model-value="(v: string) => updateCollectionField(name, 'minimum_items', v ? Number(v) : undefined)"
                          />
                        </FormField>
                        <div class="space-y-2 pt-6">
                          <Checkbox
                            :model-value="(collection as CollectionDefinition).delete_below_minimum || false"
                            @update:model-value="(v: boolean) => updateCollectionField(name, 'delete_below_minimum', v || undefined)"
                          >
                            Delete if Below Minimum
                          </Checkbox>
                          <Checkbox
                            :model-value="(collection as CollectionDefinition).delete_not_scheduled || false"
                            @update:model-value="(v: boolean) => updateCollectionField(name, 'delete_not_scheduled', v || undefined)"
                          >
                            Delete When Not Scheduled
                          </Checkbox>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Radarr Integration Section -->
                  <div class="p-4">
                    <button
                      class="w-full flex items-center justify-between text-left"
                      @click="toggleCollectionSection(name, 'radarr')"
                    >
                      <span class="font-medium flex items-center gap-2">
                        <span>🎬</span> Radarr Integration
                      </span>
                      <svg
                        class="w-5 h-5 transition-transform"
                        :class="{ 'rotate-180': isCollectionSectionExpanded(name, 'radarr') }"
                        fill="none" stroke="currentColor" viewBox="0 0 24 24"
                      >
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                      </svg>
                    </button>
                    <div v-if="isCollectionSectionExpanded(name, 'radarr')" class="mt-4 space-y-4">
                      <div class="grid grid-cols-2 gap-4">
                        <Checkbox
                          :model-value="(collection as CollectionDefinition).radarr_add_missing || false"
                          @update:model-value="(v: boolean) => updateCollectionField(name, 'radarr_add_missing', v || undefined)"
                        >
                          Add Missing Movies
                        </Checkbox>
                        <Checkbox
                          :model-value="(collection as CollectionDefinition).radarr_add_existing || false"
                          @update:model-value="(v: boolean) => updateCollectionField(name, 'radarr_add_existing', v || undefined)"
                        >
                          Add Existing Movies
                        </Checkbox>
                      </div>
                      <div class="grid grid-cols-2 gap-4">
                        <FormField label="Root Folder" tooltip="Override default root folder">
                          <Input
                            :model-value="(collection as CollectionDefinition).radarr_folder || ''"
                            placeholder="Use default"
                            @update:model-value="(v: string) => updateCollectionField(name, 'radarr_folder', v || undefined)"
                          />
                        </FormField>
                        <FormField label="Availability" tooltip="When movie is considered available">
                          <Select
                            :model-value="(collection as CollectionDefinition).radarr_availability || ''"
                            :options="[{ value: '', label: 'Use default' }, ...radarrAvailabilityOptions]"
                            @update:model-value="(v: string) => updateCollectionField(name, 'radarr_availability', v || undefined)"
                          />
                        </FormField>
                      </div>
                      <div class="grid grid-cols-2 gap-4">
                        <FormField label="Quality Profile" tooltip="Override default quality profile">
                          <Input
                            :model-value="(collection as CollectionDefinition).radarr_quality || ''"
                            placeholder="Use default"
                            @update:model-value="(v: string) => updateCollectionField(name, 'radarr_quality', v || undefined)"
                          />
                        </FormField>
                        <FormField label="Tags" tooltip="Tags to apply in Radarr">
                          <Input
                            :model-value="Array.isArray((collection as CollectionDefinition).radarr_tag) ? (collection as CollectionDefinition).radarr_tag?.join(', ') : ((collection as CollectionDefinition).radarr_tag || '')"
                            placeholder="tag1, tag2"
                            @update:model-value="(v: string) => updateCollectionField(name, 'radarr_tag', v ? v.split(',').map(s => s.trim()) : undefined)"
                          />
                        </FormField>
                      </div>
                      <div class="grid grid-cols-2 gap-4">
                        <Checkbox
                          :model-value="(collection as CollectionDefinition).radarr_monitor ?? true"
                          @update:model-value="(v: boolean) => updateCollectionField(name, 'radarr_monitor', v)"
                        >
                          Monitor Movies
                        </Checkbox>
                        <Checkbox
                          :model-value="(collection as CollectionDefinition).radarr_search || false"
                          @update:model-value="(v: boolean) => updateCollectionField(name, 'radarr_search', v || undefined)"
                        >
                          Search on Add
                        </Checkbox>
                      </div>
                    </div>
                  </div>

                  <!-- Sonarr Integration Section -->
                  <div class="p-4">
                    <button
                      class="w-full flex items-center justify-between text-left"
                      @click="toggleCollectionSection(name, 'sonarr')"
                    >
                      <span class="font-medium flex items-center gap-2">
                        <span>📺</span> Sonarr Integration
                      </span>
                      <svg
                        class="w-5 h-5 transition-transform"
                        :class="{ 'rotate-180': isCollectionSectionExpanded(name, 'sonarr') }"
                        fill="none" stroke="currentColor" viewBox="0 0 24 24"
                      >
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                      </svg>
                    </button>
                    <div v-if="isCollectionSectionExpanded(name, 'sonarr')" class="mt-4 space-y-4">
                      <div class="grid grid-cols-2 gap-4">
                        <Checkbox
                          :model-value="(collection as CollectionDefinition).sonarr_add_missing || false"
                          @update:model-value="(v: boolean) => updateCollectionField(name, 'sonarr_add_missing', v || undefined)"
                        >
                          Add Missing Shows
                        </Checkbox>
                        <Checkbox
                          :model-value="(collection as CollectionDefinition).sonarr_add_existing || false"
                          @update:model-value="(v: boolean) => updateCollectionField(name, 'sonarr_add_existing', v || undefined)"
                        >
                          Add Existing Shows
                        </Checkbox>
                      </div>
                      <div class="grid grid-cols-2 gap-4">
                        <FormField label="Root Folder" tooltip="Override default root folder">
                          <Input
                            :model-value="(collection as CollectionDefinition).sonarr_folder || ''"
                            placeholder="Use default"
                            @update:model-value="(v: string) => updateCollectionField(name, 'sonarr_folder', v || undefined)"
                          />
                        </FormField>
                        <FormField label="Monitor" tooltip="Which episodes to monitor">
                          <Select
                            :model-value="(collection as CollectionDefinition).sonarr_monitor || ''"
                            :options="[{ value: '', label: 'Use default' }, ...sonarrMonitorOptions]"
                            @update:model-value="(v: string) => updateCollectionField(name, 'sonarr_monitor', v || undefined)"
                          />
                        </FormField>
                      </div>
                      <div class="grid grid-cols-2 gap-4">
                        <FormField label="Quality Profile" tooltip="Override default quality profile">
                          <Input
                            :model-value="(collection as CollectionDefinition).sonarr_quality || ''"
                            placeholder="Use default"
                            @update:model-value="(v: string) => updateCollectionField(name, 'sonarr_quality', v || undefined)"
                          />
                        </FormField>
                        <FormField label="Language Profile" tooltip="Override default language profile">
                          <Input
                            :model-value="(collection as CollectionDefinition).sonarr_language || ''"
                            placeholder="Use default"
                            @update:model-value="(v: string) => updateCollectionField(name, 'sonarr_language', v || undefined)"
                          />
                        </FormField>
                      </div>
                      <div class="grid grid-cols-2 gap-4">
                        <FormField label="Series Type" tooltip="Type of series">
                          <Select
                            :model-value="(collection as CollectionDefinition).sonarr_series || ''"
                            :options="[
                              { value: '', label: 'Use default' },
                              { value: 'standard', label: 'Standard' },
                              { value: 'daily', label: 'Daily' },
                              { value: 'anime', label: 'Anime' },
                            ]"
                            @update:model-value="(v: string) => updateCollectionField(name, 'sonarr_series', v || undefined)"
                          />
                        </FormField>
                        <FormField label="Tags" tooltip="Tags to apply in Sonarr">
                          <Input
                            :model-value="Array.isArray((collection as CollectionDefinition).sonarr_tag) ? (collection as CollectionDefinition).sonarr_tag?.join(', ') : ((collection as CollectionDefinition).sonarr_tag || '')"
                            placeholder="tag1, tag2"
                            @update:model-value="(v: string) => updateCollectionField(name, 'sonarr_tag', v ? v.split(',').map(s => s.trim()) : undefined)"
                          />
                        </FormField>
                      </div>
                      <div class="grid grid-cols-2 gap-4">
                        <Checkbox
                          :model-value="(collection as CollectionDefinition).sonarr_season ?? true"
                          @update:model-value="(v: boolean) => updateCollectionField(name, 'sonarr_season', v)"
                        >
                          Use Season Folders
                        </Checkbox>
                        <Checkbox
                          :model-value="(collection as CollectionDefinition).sonarr_search || false"
                          @update:model-value="(v: boolean) => updateCollectionField(name, 'sonarr_search', v || undefined)"
                        >
                          Search on Add
                        </Checkbox>
                      </div>
                    </div>
                  </div>

                  <!-- Item Settings Section -->
                  <div class="p-4">
                    <button
                      class="w-full flex items-center justify-between text-left"
                      @click="toggleCollectionSection(name, 'items')"
                    >
                      <span class="font-medium flex items-center gap-2">
                        <span>📋</span> Item Settings
                      </span>
                      <svg
                        class="w-5 h-5 transition-transform"
                        :class="{ 'rotate-180': isCollectionSectionExpanded(name, 'items') }"
                        fill="none" stroke="currentColor" viewBox="0 0 24 24"
                      >
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                      </svg>
                    </button>
                    <div v-if="isCollectionSectionExpanded(name, 'items')" class="mt-4 space-y-4">
                      <FormField label="Item Labels" tooltip="Labels to apply to items in collection">
                        <Input
                          :model-value="Array.isArray((collection as CollectionDefinition).item_label) ? (collection as CollectionDefinition).item_label?.join(', ') : ((collection as CollectionDefinition).item_label || '')"
                          placeholder="label1, label2"
                          @update:model-value="(v: string) => updateCollectionField(name, 'item_label', v ? v.split(',').map(s => s.trim()) : undefined)"
                        />
                      </FormField>
                      <FormField label="Item Overlay" tooltip="Overlay to apply to items">
                        <Input
                          :model-value="(collection as CollectionDefinition).item_overlay || ''"
                          placeholder="overlay_name"
                          @update:model-value="(v: string) => updateCollectionField(name, 'item_overlay', v || undefined)"
                        />
                      </FormField>
                      <div class="grid grid-cols-3 gap-4">
                        <Checkbox
                          :model-value="(collection as CollectionDefinition).item_lock_poster || false"
                          @update:model-value="(v: boolean) => updateCollectionField(name, 'item_lock_poster', v || undefined)"
                        >
                          Lock Poster
                        </Checkbox>
                        <Checkbox
                          :model-value="(collection as CollectionDefinition).item_lock_background || false"
                          @update:model-value="(v: boolean) => updateCollectionField(name, 'item_lock_background', v || undefined)"
                        >
                          Lock Background
                        </Checkbox>
                        <Checkbox
                          :model-value="(collection as CollectionDefinition).item_lock_title || false"
                          @update:model-value="(v: boolean) => updateCollectionField(name, 'item_lock_title', v || undefined)"
                        >
                          Lock Title
                        </Checkbox>
                      </div>
                      <div class="grid grid-cols-2 gap-4">
                        <Checkbox
                          :model-value="(collection as CollectionDefinition).item_refresh || false"
                          @update:model-value="(v: boolean) => updateCollectionField(name, 'item_refresh', v || undefined)"
                        >
                          Refresh Item Metadata
                        </Checkbox>
                        <FormField label="Refresh Delay (seconds)" tooltip="Delay between item refreshes">
                          <Input
                            type="number"
                            :model-value="String((collection as CollectionDefinition).item_refresh_delay || '')"
                            placeholder="0"
                            @update:model-value="(v: string) => updateCollectionField(name, 'item_refresh_delay', v ? Number(v) : undefined)"
                          />
                        </FormField>
                      </div>
                    </div>
                  </div>

                  <!-- Advanced Section -->
                  <div class="p-4">
                    <button
                      class="w-full flex items-center justify-between text-left"
                      @click="toggleCollectionSection(name, 'advanced')"
                    >
                      <span class="font-medium flex items-center gap-2">
                        <span>🔬</span> Advanced
                      </span>
                      <svg
                        class="w-5 h-5 transition-transform"
                        :class="{ 'rotate-180': isCollectionSectionExpanded(name, 'advanced') }"
                        fill="none" stroke="currentColor" viewBox="0 0 24 24"
                      >
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                      </svg>
                    </button>
                    <div v-if="isCollectionSectionExpanded(name, 'advanced')" class="mt-4 space-y-4">
                      <div class="grid grid-cols-2 gap-4">
                        <FormField label="Run Again Delay" tooltip="Minutes to wait before re-running">
                          <Input
                            type="number"
                            :model-value="String((collection as CollectionDefinition).run_again_delay || '')"
                            placeholder="0 (no re-run)"
                            @update:model-value="(v: string) => updateCollectionField(name, 'run_again_delay', v ? Number(v) : undefined)"
                          />
                        </FormField>
                        <FormField label="Collection Filtering" tooltip="Who can filter collection">
                          <Select
                            :model-value="(collection as CollectionDefinition).collection_filtering || ''"
                            :options="[
                              { value: '', label: 'Default' },
                              { value: 'admin', label: 'Admin Only' },
                              { value: 'user', label: 'All Users' },
                            ]"
                            @update:model-value="(v: string) => updateCollectionField(name, 'collection_filtering', v || undefined)"
                          />
                        </FormField>
                      </div>
                      <div class="grid grid-cols-2 gap-4">
                        <Checkbox
                          :model-value="(collection as CollectionDefinition).missing_only_released || false"
                          @update:model-value="(v: boolean) => updateCollectionField(name, 'missing_only_released', v || undefined)"
                        >
                          Missing Only Released
                        </Checkbox>
                        <Checkbox
                          :model-value="(collection as CollectionDefinition).only_filter_missing || false"
                          @update:model-value="(v: boolean) => updateCollectionField(name, 'only_filter_missing', v || undefined)"
                        >
                          Only Filter Missing
                        </Checkbox>
                      </div>
                      <div class="grid grid-cols-2 gap-4">
                        <Checkbox
                          :model-value="(collection as CollectionDefinition).blank_collection || false"
                          @update:model-value="(v: boolean) => updateCollectionField(name, 'blank_collection', v || undefined)"
                        >
                          Allow Blank Collection
                        </Checkbox>
                        <Checkbox
                          :model-value="(collection as CollectionDefinition).build_collection ?? true"
                          @update:model-value="(v: boolean) => updateCollectionField(name, 'build_collection', v)"
                        >
                          Build Collection
                        </Checkbox>
                      </div>
                      <FormField label="Changes Webhooks" tooltip="Webhooks to call on changes">
                        <Input
                          :model-value="Array.isArray((collection as CollectionDefinition).changes_webhooks) ? (collection as CollectionDefinition).changes_webhooks?.join(', ') : ((collection as CollectionDefinition).changes_webhooks || '')"
                          placeholder="https://webhook.url"
                          @update:model-value="(v: string) => updateCollectionField(name, 'changes_webhooks', v ? v.split(',').map(s => s.trim()) : undefined)"
                        />
                      </FormField>
                      <FormField label="Server Preroll" tooltip="Preroll video to play before movies">
                        <Input
                          :model-value="(collection as CollectionDefinition).server_preroll || ''"
                          placeholder="/path/to/preroll.mp4"
                          @update:model-value="(v: string) => updateCollectionField(name, 'server_preroll', v || undefined)"
                        />
                      </FormField>
                    </div>
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

                <div class="divide-y divide-border">
                  <!-- Basic Settings Section -->
                  <div class="p-4">
                    <button
                      class="w-full flex items-center justify-between text-left"
                      @click="toggleOverlaySection(name, 'basic')"
                    >
                      <span class="font-medium flex items-center gap-2">
                        <span>⚙️</span> Basic Settings
                      </span>
                      <svg
                        class="w-5 h-5 transition-transform"
                        :class="{ 'rotate-180': isOverlaySectionExpanded(name, 'basic') }"
                        fill="none" stroke="currentColor" viewBox="0 0 24 24"
                      >
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                      </svg>
                    </button>
                    <div v-if="isOverlaySectionExpanded(name, 'basic')" class="mt-4 space-y-4">
                      <FormField label="Overlay Name/Image" tooltip="Image file, URL, or text() for dynamic text">
                        <Input
                          :model-value="(overlay as OverlayDefinition).overlay?.name || ''"
                          placeholder="image.png, text(<<resolution>>), or URL"
                          @update:model-value="(v: string) => updateOverlayField(name, 'overlay.name', v)"
                        />
                      </FormField>
                      <div class="grid grid-cols-2 gap-4">
                        <FormField label="File Path" tooltip="Local file path for overlay image">
                          <Input
                            :model-value="(overlay as OverlayDefinition).overlay?.file || ''"
                            placeholder="config/overlays/my_overlay.png"
                            @update:model-value="(v: string) => updateOverlayField(name, 'overlay.file', v || undefined)"
                          />
                        </FormField>
                        <FormField label="URL" tooltip="URL for overlay image">
                          <Input
                            :model-value="(overlay as OverlayDefinition).overlay?.url || ''"
                            placeholder="https://..."
                            @update:model-value="(v: string) => updateOverlayField(name, 'overlay.url', v || undefined)"
                          />
                        </FormField>
                      </div>
                      <div class="grid grid-cols-3 gap-4">
                        <FormField label="Weight (Priority)" tooltip="Higher weight overlays take precedence">
                          <Input
                            type="number"
                            :model-value="String((overlay as OverlayDefinition).weight || '')"
                            placeholder="10"
                            @update:model-value="(v: string) => updateOverlayField(name, 'weight', v ? Number(v) : undefined)"
                          />
                        </FormField>
                        <FormField label="Group" tooltip="Only one overlay per group is shown">
                          <Input
                            :model-value="(overlay as OverlayDefinition).group || ''"
                            placeholder="resolution"
                            @update:model-value="(v: string) => updateOverlayField(name, 'group', v || undefined)"
                          />
                        </FormField>
                        <FormField label="Queue" tooltip="Queue name for overlay processing">
                          <Input
                            :model-value="(overlay as OverlayDefinition).queue || ''"
                            placeholder="default"
                            @update:model-value="(v: string) => updateOverlayField(name, 'queue', v || undefined)"
                          />
                        </FormField>
                      </div>
                      <div class="grid grid-cols-2 gap-4">
                        <FormField label="Builder Level" tooltip="Apply to show, season, or episode level">
                          <Select
                            :model-value="(overlay as OverlayDefinition).builder_level || ''"
                            :options="[
                              { value: '', label: 'Default (Item Level)' },
                              { value: 'show', label: 'Show' },
                              { value: 'season', label: 'Season' },
                              { value: 'episode', label: 'Episode' },
                            ]"
                            @update:model-value="(v: string) => updateOverlayField(name, 'builder_level', v || undefined)"
                          />
                        </FormField>
                        <FormField label="Schedule" tooltip="When to apply this overlay">
                          <Select
                            :model-value="(overlay as OverlayDefinition).schedule || ''"
                            :options="scheduleOptions"
                            @update:model-value="(v: string) => updateOverlayField(name, 'schedule', v || undefined)"
                          />
                        </FormField>
                      </div>
                      <FormField label="Suppress Overlays" tooltip="Other overlays to hide when this one is shown">
                        <Input
                          :model-value="Array.isArray((overlay as OverlayDefinition).suppress_overlays) ? (overlay as OverlayDefinition).suppress_overlays?.join(', ') : ((overlay as OverlayDefinition).suppress_overlays || '')"
                          placeholder="overlay1, overlay2"
                          @update:model-value="(v: string) => updateOverlayField(name, 'suppress_overlays', v ? v.split(',').map(s => s.trim()) : undefined)"
                        />
                      </FormField>
                    </div>
                  </div>

                  <!-- Position Section -->
                  <div class="p-4">
                    <button
                      class="w-full flex items-center justify-between text-left"
                      @click="toggleOverlaySection(name, 'position')"
                    >
                      <span class="font-medium flex items-center gap-2">
                        <span>📍</span> Position
                      </span>
                      <svg
                        class="w-5 h-5 transition-transform"
                        :class="{ 'rotate-180': isOverlaySectionExpanded(name, 'position') }"
                        fill="none" stroke="currentColor" viewBox="0 0 24 24"
                      >
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                      </svg>
                    </button>
                    <div v-if="isOverlaySectionExpanded(name, 'position')" class="mt-4 space-y-4">
                      <div class="grid grid-cols-4 gap-4">
                        <FormField label="H. Align" tooltip="Horizontal alignment">
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
                        <FormField label="H. Offset" tooltip="Pixels from horizontal edge">
                          <Input
                            type="number"
                            :model-value="String((overlay as OverlayDefinition).overlay?.horizontal_offset || 15)"
                            @update:model-value="(v: string) => updateOverlayField(name, 'overlay.horizontal_offset', Number(v))"
                          />
                        </FormField>
                        <FormField label="V. Align" tooltip="Vertical alignment">
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
                        <FormField label="V. Offset" tooltip="Pixels from vertical edge">
                          <Input
                            type="number"
                            :model-value="String((overlay as OverlayDefinition).overlay?.vertical_offset || 15)"
                            @update:model-value="(v: string) => updateOverlayField(name, 'overlay.vertical_offset', Number(v))"
                          />
                        </FormField>
                      </div>
                      <p class="text-xs text-content-muted">Or use exact coordinates:</p>
                      <div class="grid grid-cols-4 gap-4">
                        <FormField label="X Coordinate" tooltip="Exact X position in pixels">
                          <Input
                            type="number"
                            :model-value="String((overlay as OverlayDefinition).overlay?.x_coordinate || '')"
                            placeholder="Auto"
                            @update:model-value="(v: string) => updateOverlayField(name, 'overlay.x_coordinate', v ? Number(v) : undefined)"
                          />
                        </FormField>
                        <FormField label="X Align" tooltip="Alignment relative to X coordinate">
                          <Select
                            :model-value="(overlay as OverlayDefinition).overlay?.x_align || ''"
                            :options="[
                              { value: '', label: 'Default' },
                              { value: 'left', label: 'Left' },
                              { value: 'center', label: 'Center' },
                              { value: 'right', label: 'Right' },
                            ]"
                            @update:model-value="(v: string) => updateOverlayField(name, 'overlay.x_align', v || undefined)"
                          />
                        </FormField>
                        <FormField label="Y Coordinate" tooltip="Exact Y position in pixels">
                          <Input
                            type="number"
                            :model-value="String((overlay as OverlayDefinition).overlay?.y_coordinate || '')"
                            placeholder="Auto"
                            @update:model-value="(v: string) => updateOverlayField(name, 'overlay.y_coordinate', v ? Number(v) : undefined)"
                          />
                        </FormField>
                        <FormField label="Y Align" tooltip="Alignment relative to Y coordinate">
                          <Select
                            :model-value="(overlay as OverlayDefinition).overlay?.y_align || ''"
                            :options="[
                              { value: '', label: 'Default' },
                              { value: 'top', label: 'Top' },
                              { value: 'center', label: 'Center' },
                              { value: 'bottom', label: 'Bottom' },
                            ]"
                            @update:model-value="(v: string) => updateOverlayField(name, 'overlay.y_align', v || undefined)"
                          />
                        </FormField>
                      </div>
                    </div>
                  </div>

                  <!-- Font Settings Section -->
                  <div class="p-4">
                    <button
                      class="w-full flex items-center justify-between text-left"
                      @click="toggleOverlaySection(name, 'font')"
                    >
                      <span class="font-medium flex items-center gap-2">
                        <span>🔤</span> Font Settings
                      </span>
                      <svg
                        class="w-5 h-5 transition-transform"
                        :class="{ 'rotate-180': isOverlaySectionExpanded(name, 'font') }"
                        fill="none" stroke="currentColor" viewBox="0 0 24 24"
                      >
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                      </svg>
                    </button>
                    <div v-if="isOverlaySectionExpanded(name, 'font')" class="mt-4 space-y-4">
                      <div class="grid grid-cols-2 gap-4">
                        <FormField label="Font" tooltip="Font name or path to .ttf file">
                          <Input
                            :model-value="(overlay as OverlayDefinition).overlay?.font || ''"
                            placeholder="fonts/Inter-Bold.ttf"
                            @update:model-value="(v: string) => updateOverlayField(name, 'overlay.font', v || undefined)"
                          />
                        </FormField>
                        <FormField label="Font Style" tooltip="Font style (if using system font)">
                          <Input
                            :model-value="(overlay as OverlayDefinition).overlay?.font_style || ''"
                            placeholder="Bold, Italic"
                            @update:model-value="(v: string) => updateOverlayField(name, 'overlay.font_style', v || undefined)"
                          />
                        </FormField>
                      </div>
                      <div class="grid grid-cols-3 gap-4">
                        <FormField label="Font Size" tooltip="Font size in pixels">
                          <Input
                            type="number"
                            :model-value="String((overlay as OverlayDefinition).overlay?.font_size || '')"
                            placeholder="55"
                            @update:model-value="(v: string) => updateOverlayField(name, 'overlay.font_size', v ? Number(v) : undefined)"
                          />
                        </FormField>
                        <FormField label="Font Color" tooltip="Hex color code for text">
                          <Input
                            :model-value="(overlay as OverlayDefinition).overlay?.font_color || ''"
                            placeholder="#FFFFFF"
                            @update:model-value="(v: string) => updateOverlayField(name, 'overlay.font_color', v || undefined)"
                          />
                        </FormField>
                        <FormField label="Preview">
                          <div
                            class="h-9 rounded border border-border flex items-center justify-center text-sm"
                            :style="{ color: (overlay as OverlayDefinition).overlay?.font_color || '#FFFFFF' }"
                          >
                            Sample Text
                          </div>
                        </FormField>
                      </div>
                      <div class="grid grid-cols-2 gap-4">
                        <FormField label="Stroke Color" tooltip="Hex color for text outline">
                          <Input
                            :model-value="(overlay as OverlayDefinition).overlay?.stroke_color || ''"
                            placeholder="#000000"
                            @update:model-value="(v: string) => updateOverlayField(name, 'overlay.stroke_color', v || undefined)"
                          />
                        </FormField>
                        <FormField label="Stroke Width" tooltip="Stroke width in pixels">
                          <Input
                            type="number"
                            :model-value="String((overlay as OverlayDefinition).overlay?.stroke_width || '')"
                            placeholder="0"
                            @update:model-value="(v: string) => updateOverlayField(name, 'overlay.stroke_width', v ? Number(v) : undefined)"
                          />
                        </FormField>
                      </div>
                    </div>
                  </div>

                  <!-- Background Settings Section -->
                  <div class="p-4">
                    <button
                      class="w-full flex items-center justify-between text-left"
                      @click="toggleOverlaySection(name, 'background')"
                    >
                      <span class="font-medium flex items-center gap-2">
                        <span>🎨</span> Background
                      </span>
                      <svg
                        class="w-5 h-5 transition-transform"
                        :class="{ 'rotate-180': isOverlaySectionExpanded(name, 'background') }"
                        fill="none" stroke="currentColor" viewBox="0 0 24 24"
                      >
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                      </svg>
                    </button>
                    <div v-if="isOverlaySectionExpanded(name, 'background')" class="mt-4 space-y-4">
                      <div class="grid grid-cols-3 gap-4">
                        <FormField label="Back Color" tooltip="Background color (hex with alpha)">
                          <Input
                            :model-value="(overlay as OverlayDefinition).overlay?.back_color || ''"
                            placeholder="#00000099"
                            @update:model-value="(v: string) => updateOverlayField(name, 'overlay.back_color', v || undefined)"
                          />
                        </FormField>
                        <FormField label="Back Width" tooltip="Background width in pixels">
                          <Input
                            type="number"
                            :model-value="String((overlay as OverlayDefinition).overlay?.back_width || '')"
                            placeholder="Auto"
                            @update:model-value="(v: string) => updateOverlayField(name, 'overlay.back_width', v ? Number(v) : undefined)"
                          />
                        </FormField>
                        <FormField label="Back Height" tooltip="Background height in pixels">
                          <Input
                            type="number"
                            :model-value="String((overlay as OverlayDefinition).overlay?.back_height || '')"
                            placeholder="Auto"
                            @update:model-value="(v: string) => updateOverlayField(name, 'overlay.back_height', v ? Number(v) : undefined)"
                          />
                        </FormField>
                      </div>
                      <div class="grid grid-cols-3 gap-4">
                        <FormField label="Back Radius" tooltip="Corner radius in pixels">
                          <Input
                            type="number"
                            :model-value="String((overlay as OverlayDefinition).overlay?.back_radius || '')"
                            placeholder="0"
                            @update:model-value="(v: string) => updateOverlayField(name, 'overlay.back_radius', v ? Number(v) : undefined)"
                          />
                        </FormField>
                        <FormField label="Back Padding" tooltip="Padding inside background">
                          <Input
                            type="number"
                            :model-value="String((overlay as OverlayDefinition).overlay?.back_padding || '')"
                            placeholder="0"
                            @update:model-value="(v: string) => updateOverlayField(name, 'overlay.back_padding', v ? Number(v) : undefined)"
                          />
                        </FormField>
                        <FormField label="Back Align" tooltip="Text alignment within background">
                          <Select
                            :model-value="(overlay as OverlayDefinition).overlay?.back_align || ''"
                            :options="[
                              { value: '', label: 'Default' },
                              { value: 'left', label: 'Left' },
                              { value: 'center', label: 'Center' },
                              { value: 'right', label: 'Right' },
                            ]"
                            @update:model-value="(v: string) => updateOverlayField(name, 'overlay.back_align', v || undefined)"
                          />
                        </FormField>
                      </div>
                      <div class="grid grid-cols-2 gap-4">
                        <FormField label="Back Line Color" tooltip="Border color for background">
                          <Input
                            :model-value="(overlay as OverlayDefinition).overlay?.back_line_color || ''"
                            placeholder="#FFFFFF"
                            @update:model-value="(v: string) => updateOverlayField(name, 'overlay.back_line_color', v || undefined)"
                          />
                        </FormField>
                        <FormField label="Back Line Width" tooltip="Border width in pixels">
                          <Input
                            type="number"
                            :model-value="String((overlay as OverlayDefinition).overlay?.back_line_width || '')"
                            placeholder="0"
                            @update:model-value="(v: string) => updateOverlayField(name, 'overlay.back_line_width', v ? Number(v) : undefined)"
                          />
                        </FormField>
                      </div>
                    </div>
                  </div>

                  <!-- Addon Settings Section -->
                  <div class="p-4">
                    <button
                      class="w-full flex items-center justify-between text-left"
                      @click="toggleOverlaySection(name, 'addon')"
                    >
                      <span class="font-medium flex items-center gap-2">
                        <span>➕</span> Addon Settings
                      </span>
                      <svg
                        class="w-5 h-5 transition-transform"
                        :class="{ 'rotate-180': isOverlaySectionExpanded(name, 'addon') }"
                        fill="none" stroke="currentColor" viewBox="0 0 24 24"
                      >
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                      </svg>
                    </button>
                    <div v-if="isOverlaySectionExpanded(name, 'addon')" class="mt-4 space-y-4">
                      <p class="text-sm text-content-secondary">
                        Addon settings control how multiple overlay elements are combined.
                      </p>
                      <div class="grid grid-cols-2 gap-4">
                        <FormField label="Addon Offset" tooltip="Space between addon elements">
                          <Input
                            type="number"
                            :model-value="String((overlay as OverlayDefinition).overlay?.addon_offset || '')"
                            placeholder="0"
                            @update:model-value="(v: string) => updateOverlayField(name, 'overlay.addon_offset', v ? Number(v) : undefined)"
                          />
                        </FormField>
                        <FormField label="Addon Position" tooltip="Where addon appears relative to main">
                          <Select
                            :model-value="(overlay as OverlayDefinition).overlay?.addon_position || ''"
                            :options="[
                              { value: '', label: 'Default' },
                              { value: 'left', label: 'Left' },
                              { value: 'right', label: 'Right' },
                              { value: 'top', label: 'Top' },
                              { value: 'bottom', label: 'Bottom' },
                            ]"
                            @update:model-value="(v: string) => updateOverlayField(name, 'overlay.addon_position', v || undefined)"
                          />
                        </FormField>
                      </div>
                      <FormField label="PMM Overlay" tooltip="Use a pre-made PMM overlay">
                        <Input
                          :model-value="(overlay as OverlayDefinition).overlay?.pmm || ''"
                          placeholder="resolution/4k"
                          @update:model-value="(v: string) => updateOverlayField(name, 'overlay.pmm', v || undefined)"
                        />
                      </FormField>
                    </div>
                  </div>

                  <!-- Builder Section -->
                  <div class="p-4">
                    <button
                      class="w-full flex items-center justify-between text-left"
                      @click="toggleOverlaySection(name, 'builder')"
                    >
                      <span class="font-medium flex items-center gap-2">
                        <span>🔧</span> Builder
                      </span>
                      <svg
                        class="w-5 h-5 transition-transform"
                        :class="{ 'rotate-180': isOverlaySectionExpanded(name, 'builder') }"
                        fill="none" stroke="currentColor" viewBox="0 0 24 24"
                      >
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                      </svg>
                    </button>
                    <div v-if="isOverlaySectionExpanded(name, 'builder')" class="mt-4 space-y-4">
                      <p class="text-sm text-content-secondary">
                        Select which items this overlay applies to. Use plex_all for all items or specify filters.
                      </p>
                      <div class="space-y-2">
                        <Checkbox
                          :model-value="(overlay as OverlayDefinition).plex_all || false"
                          @update:model-value="(v: boolean) => updateOverlayField(name, 'plex_all', v || undefined)"
                        >
                          Apply to All Items (plex_all)
                        </Checkbox>
                      </div>
                      <FormField label="TMDb List" tooltip="TMDb list IDs to match">
                        <Input
                          :model-value="Array.isArray((overlay as OverlayDefinition).tmdb_list) ? (overlay as OverlayDefinition).tmdb_list?.join(', ') : ((overlay as OverlayDefinition).tmdb_list || '')"
                          placeholder="List ID or URL"
                          @update:model-value="(v: string) => updateOverlayField(name, 'tmdb_list', v || undefined)"
                        />
                      </FormField>
                      <FormField label="IMDb List" tooltip="IMDb list URLs to match">
                        <Input
                          :model-value="Array.isArray((overlay as OverlayDefinition).imdb_list) ? (overlay as OverlayDefinition).imdb_list?.join(', ') : ((overlay as OverlayDefinition).imdb_list || '')"
                          placeholder="IMDb list URL"
                          @update:model-value="(v: string) => updateOverlayField(name, 'imdb_list', v || undefined)"
                        />
                      </FormField>
                      <FormField label="Trakt List" tooltip="Trakt list URLs to match">
                        <Input
                          :model-value="Array.isArray((overlay as OverlayDefinition).trakt_list) ? (overlay as OverlayDefinition).trakt_list?.join(', ') : ((overlay as OverlayDefinition).trakt_list || '')"
                          placeholder="Trakt list URL"
                          @update:model-value="(v: string) => updateOverlayField(name, 'trakt_list', v || undefined)"
                        />
                      </FormField>
                      <FormField label="MDBList" tooltip="MDBList list URLs to match">
                        <Input
                          :model-value="Array.isArray((overlay as OverlayDefinition).mdblist_list) ? (overlay as OverlayDefinition).mdblist_list?.join(', ') : ((overlay as OverlayDefinition).mdblist_list || '')"
                          placeholder="MDBList URL"
                          @update:model-value="(v: string) => updateOverlayField(name, 'mdblist_list', v || undefined)"
                        />
                      </FormField>
                    </div>
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
          <p v-if="selectedBuilderDescription" class="mt-2 text-sm text-content-secondary">
            {{ selectedBuilderDescription }}
          </p>
        </FormField>

        <FormField
          v-if="newCollectionBuilder === 'imdb_chart'"
          label="IMDb Chart"
        >
          <Select
            v-model="newCollectionBuilderValue"
            :options="imdbChartOptions"
          />
          <p v-if="imdbChartOptions.find(o => o.value === newCollectionBuilderValue)?.description" class="mt-2 text-sm text-content-secondary">
            {{ imdbChartOptions.find(o => o.value === newCollectionBuilderValue)?.description }}
          </p>
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
          <p v-if="selectedOverlayDescription" class="mt-2 text-sm text-content-secondary">
            {{ selectedOverlayDescription }}
          </p>
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
