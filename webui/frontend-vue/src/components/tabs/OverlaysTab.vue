<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useOverlayList, useGenerateOverlayPreview, useGenerateConfigOverlayPreview, useMediaSearch } from '@/api';
import { useConfigStore } from '@/stores';
import { useToast } from '@/composables';
import { Card, Button, Input, Select, Spinner, Badge, ParityStatusBadge } from '@/components/common';
import type { OverlayPreviewResponse } from '@/types';

const toast = useToast();
const configStore = useConfigStore();

// Fetch overlay list
const { data: overlays, isLoading: overlaysLoading } = useOverlayList();

// Get libraries from config store (reflects current editor content)
// Auto-select first library if available
const selectedLibrary = ref<string>('');

// Watch for libraries to become available and auto-select first one
watch(() => configStore.libraries, (libs) => {
  if (libs.length > 0 && !selectedLibrary.value) {
    selectedLibrary.value = libs[0];
  }
}, { immediate: true });

// Library options for the selector - uses config store's libraries computed
const libraryOptions = computed(() => {
  const options = [{ value: '', label: 'Select a library...' }];
  for (const lib of configStore.libraries) {
    options.push({ value: lib, label: lib });
  }
  return options;
});

// Filter and group state
const overlaySearch = ref('');
const selectedGroup = ref('all');
const viewMode = ref<'grid' | 'list'>('grid');

// Extract overlay groups from overlay names
const overlayGroups = computed(() => {
  if (!overlays.value?.overlays) return [];
  const groups = new Set<string>();

  overlays.value.overlays.forEach((name: string) => {
    // Extract group from overlay name (e.g., "resolution/4k" -> "resolution")
    const parts = name.split('/');
    if (parts.length > 1) {
      groups.add(parts[0]);
    }
  });

  return ['all', ...Array.from(groups).sort()];
});

// Filtered overlays based on search and group
const filteredOverlays = computed(() => {
  if (!overlays.value?.overlays) return [];

  let result = overlays.value.overlays;

  // Filter by group
  if (selectedGroup.value !== 'all') {
    result = result.filter((name: string) => name.startsWith(selectedGroup.value + '/'));
  }

  // Filter by search query
  if (overlaySearch.value) {
    const query = overlaySearch.value.toLowerCase();
    result = result.filter((name: string) => name.toLowerCase().includes(query));
  }

  return result;
});

// Grouped overlays for display
const groupedOverlays = computed(() => {
  const groups: Record<string, string[]> = {};

  filteredOverlays.value.forEach((name: string) => {
    const parts = name.split('/');
    const group = parts.length > 1 ? parts[0] : 'Other';
    if (!groups[group]) groups[group] = [];
    groups[group].push(name);
  });

  return groups;
});

// Preview state
const selectedOverlay = ref('');
const searchQuery = ref('');
const selectedMedia = ref('');
const selectedMediaTmdbId = ref('');  // Store TMDb ID when available
const posterSource = ref<'tmdb' | 'plex'>('tmdb');  // Default to TMDb clean poster
const previewResult = ref<OverlayPreviewResponse | null>(null);
const isGenerating = ref(false);
const showParityDetails = ref(false);

// Poster source options
const posterSourceOptions = [
  { value: 'tmdb', label: 'TMDb (Clean)' },
  { value: 'plex', label: 'Plex (Current)' },
];

// Media search for preview - reactive params
const { data: mediaResults, isLoading: mediaLoading } = useMediaSearch(
  computed(() => ({
    query: searchQuery.value,
    limit: 10,
  }))
);

// Generate preview mutations
const generatePreview = useGenerateOverlayPreview();
const generateConfigPreview = useGenerateConfigOverlayPreview();

// Computed preview URL (backwards compatible)
const previewUrl = computed(() => previewResult.value?.image || '');

// Computed parity info
const parityInfo = computed(() => previewResult.value?.parity);

// Check if config is loaded from the store
const hasConfigLoaded = computed(() => !!configStore.rawConfig && configStore.rawConfig.length > 0);

// Check if we can generate from config (need library selected and media selected)
const canGenerateFromConfig = computed(() => {
  return hasConfigLoaded.value && selectedLibrary.value && selectedMedia.value;
});

// Handle generate preview from config (uses all overlays configured for the library)
const handleGenerateFromConfig = async () => {
  if (!selectedLibrary.value) {
    toast.warning('Please select a library');
    return;
  }
  if (!selectedMedia.value) {
    toast.warning('Please select a media item');
    return;
  }

  isGenerating.value = true;
  previewResult.value = null;

  try {
    console.log('[OverlaysTab] Generating from config:', {
      library: selectedLibrary.value,
      media_id: selectedMedia.value,
      poster_source: posterSource.value,
      config_content_length: configStore.rawConfig?.length || 0,
    });

    const result = await generateConfigPreview.mutateAsync({
      media_id: selectedMedia.value,
      library: selectedLibrary.value,
      poster_source: posterSource.value,
      config_content: configStore.rawConfig || undefined,
    });

    console.log('[OverlaysTab] Config preview result:', result);
    previewResult.value = result as unknown as OverlayPreviewResponse;
    toast.success('Preview generated from config');
  } catch (err: unknown) {
    console.error('[OverlaysTab] Config preview error:', err);
    const errorMessage = err instanceof Error ? err.message : 'Unknown error';
    toast.error(`Failed to generate preview: ${errorMessage}`);
  } finally {
    isGenerating.value = false;
  }
};

// Handle generate preview for a single overlay (optional - for testing individual overlays)
const handleGeneratePreview = async () => {
  if (!selectedOverlay.value || !selectedMedia.value) {
    toast.warning('Please select an overlay and a media item');
    return;
  }

  isGenerating.value = true;
  previewResult.value = null;

  try {
    const result = await generatePreview.mutateAsync({
      overlay_name: selectedOverlay.value,
      media_id: selectedMedia.value,
      poster_source: posterSource.value,
      library: selectedLibrary.value || undefined,
      config_content: configStore.rawConfig || undefined,
    });

    previewResult.value = result as unknown as OverlayPreviewResponse;
    toast.success('Preview generated');
  } catch (err: unknown) {
    console.error('[OverlaysTab] Preview error:', err);
    const errorMessage = err instanceof Error ? err.message : 'Unknown error';
    toast.error(`Failed to generate preview: ${errorMessage}`);
  } finally {
    isGenerating.value = false;
  }
};

// Get variable source icon
const getSourceIcon = (source: string) => {
  if (source.includes('Plex')) return 'M19.5 12c0-1.232-.046-2.453-.138-3.662a4.006 4.006 0 00-3.7-3.7 48.678 48.678 0 00-7.324 0 4.006 4.006 0 00-3.7 3.7c-.017.22-.032.441-.046.662M19.5 12l3-3m-3 3l-3-3m-12 3c0 1.232.046 2.453.138 3.662a4.006 4.006 0 003.7 3.7 48.656 48.656 0 007.324 0 4.006 4.006 0 003.7-3.7c.017-.22.032-.441.046-.662M4.5 12l3 3m-3-3l-3 3';
  if (source.includes('Sample')) return 'M9.879 7.519c1.171-1.025 3.071-1.025 4.242 0 1.172 1.025 1.172 2.687 0 3.712-.203.179-.43.326-.67.442-.745.361-1.45.999-1.45 1.827v.75M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9 5.25h.008v.008H12v-.008z';
  return 'M4.5 12a7.5 7.5 0 0015 0m-15 0a7.5 7.5 0 1115 0m-15 0H3m16.5 0H21';
};

// Get display name for overlay (remove group prefix)
const getDisplayName = (name: string) => {
  const parts = name.split('/');
  return parts.length > 1 ? parts.slice(1).join('/') : name;
};
</script>

<template>
  <div class="h-full flex flex-col gap-4">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-xl font-semibold text-content-primary">
          Overlay Preview
        </h2>
        <p class="text-sm text-content-secondary mt-0.5">
          Preview how overlays will appear on your media posters
        </p>
      </div>

      <!-- View toggle -->
      <div class="flex items-center gap-2">
        <span class="text-sm text-content-muted">
          {{ filteredOverlays.length }} overlays
        </span>
        <div class="flex items-center bg-surface-tertiary rounded-md p-0.5">
          <button
            type="button"
            :class="[
              'p-1.5 rounded transition-colors',
              viewMode === 'grid' ? 'bg-surface-primary shadow-sm' : 'text-content-muted hover:text-content'
            ]"
            title="Grid view"
            @click="viewMode = 'grid'"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"/>
            </svg>
          </button>
          <button
            type="button"
            :class="[
              'p-1.5 rounded transition-colors',
              viewMode === 'list' ? 'bg-surface-primary shadow-sm' : 'text-content-muted hover:text-content'
            ]"
            title="List view"
            @click="viewMode = 'list'"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16"/>
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="flex items-center gap-4">
      <div class="flex-1">
        <Input
          v-model="overlaySearch"
          type="search"
          placeholder="Search overlays..."
        />
      </div>
      <div class="w-48">
        <Select
          v-model="selectedGroup"
          :options="overlayGroups.map(g => ({ value: g, label: g === 'all' ? 'All Groups' : g }))"
          placeholder="Filter by group"
        />
      </div>
    </div>

    <div class="flex-1 grid grid-cols-1 lg:grid-cols-2 gap-4 min-h-0 overflow-hidden">
      <!-- Overlay List -->
      <Card class="flex flex-col min-h-0" padding="none">
        <template #header>
          <span class="font-medium">Available Overlays</span>
        </template>

        <div v-if="overlaysLoading" class="flex-1 flex items-center justify-center p-8">
          <Spinner size="lg" />
        </div>

        <div v-else-if="filteredOverlays.length === 0" class="flex-1 flex items-center justify-center p-8 text-content-muted">
          <div class="text-center">
            <svg class="w-12 h-12 mx-auto mb-2 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
            </svg>
            <p>No overlays found</p>
            <p class="text-xs mt-2">
              Overlays are loaded from the Kometa defaults directory.
              <br>
              Ensure KOMETA_ROOT is set correctly.
            </p>
          </div>
        </div>

        <div v-else class="flex-1 overflow-auto p-2">
          <!-- Grid View -->
          <div v-if="viewMode === 'grid'" class="space-y-4">
            <div
              v-for="(items, group) in groupedOverlays"
              :key="group"
            >
              <h4 class="text-xs font-medium text-content-muted uppercase tracking-wide px-2 mb-2">
                {{ group }}
              </h4>
              <div class="grid grid-cols-2 gap-2">
                <button
                  v-for="name in items"
                  :key="name"
                  type="button"
                  :class="[
                    'p-3 rounded-lg text-left transition-colors border',
                    selectedOverlay === name
                      ? 'border-kometa-gold bg-kometa-gold/10'
                      : 'border-transparent bg-surface-tertiary hover:bg-surface-hover'
                  ]"
                  @click="selectedOverlay = name"
                >
                  <div class="font-medium text-sm truncate">
                    {{ getDisplayName(name) }}
                  </div>
                </button>
              </div>
            </div>
          </div>

          <!-- List View -->
          <div v-else class="space-y-1">
            <button
              v-for="name in filteredOverlays"
              :key="name"
              type="button"
              :class="[
                'w-full flex items-center gap-3 p-2 rounded-md text-left transition-colors',
                selectedOverlay === name
                  ? 'bg-kometa-gold/10 text-kometa-gold'
                  : 'hover:bg-surface-tertiary'
              ]"
              @click="selectedOverlay = name"
            >
              <svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
              </svg>
              <span class="text-sm font-medium truncate flex-1">{{ name }}</span>
              <Badge v-if="name.includes('/')" variant="default" size="sm">
                {{ name.split('/')[0] }}
              </Badge>
            </button>
          </div>
        </div>
      </Card>

      <!-- Preview Panel -->
      <div class="flex flex-col gap-4 min-h-0">
        <!-- Media Search -->
        <Card>
          <template #header>
            <span class="font-medium">Select Media</span>
          </template>

          <div class="space-y-3">
            <Input
              v-model="searchQuery"
              type="search"
              placeholder="Search for a movie or show..."
            />

            <div
              v-if="mediaLoading"
              class="flex items-center justify-center py-4"
            >
              <Spinner size="sm" />
            </div>

            <!-- Show error if search returned an error -->
            <div
              v-else-if="mediaResults && 'error' in mediaResults && (mediaResults as { error: string }).error"
              class="p-3 rounded-md bg-amber-500/10 border border-amber-500/30 text-amber-200 text-sm"
            >
              <p class="font-medium">Search unavailable</p>
              <p class="text-xs mt-1 opacity-80">{{ (mediaResults as { error: string }).error }}</p>
            </div>

            <div
              v-else-if="mediaResults?.items?.length"
              class="space-y-1 max-h-32 overflow-auto"
            >
              <button
                v-for="item in mediaResults.items"
                :key="item.id"
                type="button"
                :class="[
                  'w-full flex items-center gap-3 p-2 rounded-md text-left transition-colors',
                  selectedMedia === item.id
                    ? 'bg-kometa-gold/10 text-kometa-gold'
                    : 'hover:bg-surface-tertiary',
                ]"
                @click="selectedMedia = item.id"
              >
                <img
                  v-if="item.poster_url"
                  :src="item.poster_url"
                  :alt="item.title"
                  class="w-6 h-9 object-cover rounded"
                >
                <div
                  v-else
                  class="w-6 h-9 bg-surface-tertiary rounded"
                />
                <div class="flex-1 min-w-0">
                  <div class="font-medium text-xs truncate">
                    {{ item.title }}
                  </div>
                  <div class="text-xs text-content-muted">
                    {{ item.year }}
                  </div>
                </div>
              </button>
            </div>

            <!-- Poster Source Selector -->
            <div class="flex items-center gap-2">
              <span class="text-xs text-content-muted whitespace-nowrap">Poster:</span>
              <Select
                v-model="posterSource"
                :options="posterSourceOptions"
                size="sm"
                class="flex-1"
              />
            </div>

            <!-- Library Config Selector (for template_variables) -->
            <div v-if="configStore.libraries.length > 0" class="flex items-center gap-2">
              <span class="text-xs text-content-muted whitespace-nowrap">Config:</span>
              <Select
                v-model="selectedLibrary"
                :options="libraryOptions"
                size="sm"
                class="flex-1"
              />
            </div>

            <!-- Config status indicator -->
            <div class="flex items-center gap-2 text-xs">
              <span
                :class="[
                  'w-2 h-2 rounded-full',
                  hasConfigLoaded ? 'bg-emerald-500' : 'bg-amber-500'
                ]"
              />
              <span class="text-content-muted">
                {{ hasConfigLoaded ? 'Using editor config' : 'No config loaded' }}
              </span>
            </div>

            <!-- Generate buttons -->
            <div class="space-y-2">
              <!-- Primary: Generate from Config (uses all overlays configured for library) -->
              <Button
                class="w-full"
                :loading="isGenerating"
                :disabled="!canGenerateFromConfig"
                @click="handleGenerateFromConfig"
              >
                Preview from Config
              </Button>

              <!-- Secondary: Generate single overlay (optional, for testing) -->
              <Button
                v-if="selectedOverlay"
                variant="secondary"
                class="w-full"
                :loading="isGenerating"
                :disabled="!selectedOverlay || !selectedMedia"
                @click="handleGeneratePreview"
              >
                Preview "{{ selectedOverlay }}" Only
              </Button>
            </div>

            <!-- Help text -->
            <p class="text-xs text-content-muted">
              <template v-if="!selectedLibrary">
                Select a library above to preview overlays from your config.
              </template>
              <template v-else-if="!selectedMedia">
                Search and select a media item to preview.
              </template>
              <template v-else>
                Click "Preview from Config" to see all overlays configured for {{ selectedLibrary }}.
              </template>
            </p>
          </div>
        </Card>

        <!-- Preview -->
        <Card class="flex-1 flex flex-col min-h-0">
          <template #header>
            <div class="flex items-center justify-between w-full">
              <span class="font-medium">Preview</span>
              <ParityStatusBadge
                v-if="parityInfo"
                :status="parityInfo.status"
              />
            </div>
          </template>

          <div class="flex-1 flex flex-col gap-3">
            <!-- Preview Image -->
            <div class="flex-1 flex items-center justify-center bg-surface-tertiary rounded-lg min-h-[200px]">
              <img
                v-if="previewUrl"
                :src="previewUrl"
                alt="Overlay preview"
                class="max-w-full max-h-full object-contain rounded"
              >
              <div
                v-else
                class="text-center text-content-muted"
              >
                <svg
                  class="w-12 h-12 mx-auto mb-2 opacity-50"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                  />
                </svg>
                <p class="text-sm">Select an overlay and media</p>
                <p class="text-xs">to generate a preview</p>
              </div>
            </div>

            <!-- Parity Details (collapsible) -->
            <div v-if="parityInfo" class="border-t border-border pt-3">
              <button
                type="button"
                class="w-full flex items-center justify-between text-sm text-content-muted hover:text-content transition-colors"
                @click="showParityDetails = !showParityDetails"
              >
                <span class="flex items-center gap-2">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Preview Parity Details
                </span>
                <svg
                  :class="['w-4 h-4 transition-transform', showParityDetails ? 'rotate-180' : '']"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              <div v-if="showParityDetails" class="mt-3 space-y-3 text-xs">
                <!-- Parity Status Details -->
                <div v-if="parityInfo.details.length > 0">
                  <h5 class="font-medium text-content-secondary mb-1">Status Notes</h5>
                  <ul class="space-y-1 text-content-muted">
                    <li
                      v-for="(detail, idx) in parityInfo.details"
                      :key="idx"
                      class="flex items-start gap-2"
                    >
                      <span class="text-amber-400 mt-0.5">•</span>
                      <span>{{ detail }}</span>
                    </li>
                  </ul>
                </div>

                <!-- Variable Log -->
                <div v-if="parityInfo.variable_log.length > 0">
                  <h5 class="font-medium text-content-secondary mb-1">Variable Resolution</h5>
                  <div class="space-y-1">
                    <div
                      v-for="(variable, idx) in parityInfo.variable_log"
                      :key="idx"
                      class="flex items-center gap-2 text-content-muted"
                    >
                      <svg class="w-3.5 h-3.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="getSourceIcon(variable.source)" />
                      </svg>
                      <code class="text-kometa-gold">{{ variable.variable }}</code>
                      <span class="text-content-muted">=</span>
                      <span :class="variable.is_real ? 'text-emerald-400' : 'text-amber-400'">
                        {{ variable.value }}
                      </span>
                      <span class="text-content-muted text-[10px]">({{ variable.source }})</span>
                    </div>
                  </div>
                </div>

                <!-- Group Decisions -->
                <div v-if="parityInfo.group_decisions.length > 0">
                  <h5 class="font-medium text-content-secondary mb-1">Group Selection</h5>
                  <div class="space-y-2">
                    <div
                      v-for="(decision, idx) in parityInfo.group_decisions"
                      :key="idx"
                      class="bg-surface-tertiary rounded p-2"
                    >
                      <div class="flex items-center gap-2">
                        <Badge variant="success" size="sm">{{ decision.group_name }}</Badge>
                        <span class="text-content-muted">Winner:</span>
                        <span class="font-medium text-emerald-400">{{ decision.winner }}</span>
                        <span class="text-content-muted">(weight {{ decision.winner_weight }})</span>
                      </div>
                      <div v-if="decision.losers.length > 0" class="mt-1 text-content-muted">
                        Excluded: {{ decision.losers.map(l => `${l.name} (${l.weight})`).join(', ') }}
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Queue Assignments -->
                <div v-if="parityInfo.queue_assignments.length > 0">
                  <h5 class="font-medium text-content-secondary mb-1">Queue Positions</h5>
                  <div class="space-y-1">
                    <div
                      v-for="(assignment, idx) in parityInfo.queue_assignments"
                      :key="idx"
                      class="flex items-center gap-2 text-content-muted"
                    >
                      <Badge variant="info" size="sm">{{ assignment.queue_name }}</Badge>
                      <span>Position {{ assignment.position_index + 1 }}:</span>
                      <span class="text-content">{{ assignment.overlay_name }}</span>
                      <span class="text-[10px]">(weight {{ assignment.weight }})</span>
                    </div>
                  </div>
                </div>

                <!-- Suppressed Overlays -->
                <div v-if="parityInfo.suppressed_overlays.length > 0">
                  <h5 class="font-medium text-content-secondary mb-1">Suppressed Overlays</h5>
                  <div class="space-y-1">
                    <div
                      v-for="(suppressed, idx) in parityInfo.suppressed_overlays"
                      :key="idx"
                      class="flex items-center gap-2 text-content-muted"
                    >
                      <span class="text-red-400">{{ suppressed.suppressed }}</span>
                      <span>suppressed by</span>
                      <span class="text-emerald-400">{{ suppressed.suppressor }}</span>
                    </div>
                  </div>
                </div>

                <!-- Warnings -->
                <div v-if="previewResult?.warnings && previewResult.warnings.length > 0">
                  <h5 class="font-medium text-content-secondary mb-1">Warnings</h5>
                  <ul class="space-y-1 text-amber-400">
                    <li
                      v-for="(warning, idx) in previewResult.warnings"
                      :key="idx"
                      class="flex items-start gap-2"
                    >
                      <svg class="w-3.5 h-3.5 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                      </svg>
                      <span>{{ warning }}</span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  </div>
</template>
