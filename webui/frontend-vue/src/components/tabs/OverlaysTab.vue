<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useOverlayList, useGenerateOverlayPreview, useMediaSearch } from '@/api';
import { useToast } from '@/composables';
import { Card, Button, Input, Select, Spinner, Badge } from '@/components/common';

const toast = useToast();

// Fetch overlay list
const { data: overlays, isLoading: overlaysLoading } = useOverlayList();

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
const previewUrl = ref('');
const isGenerating = ref(false);

// Media search for preview
const { data: mediaResults, isLoading: mediaLoading } = useMediaSearch({
  query: searchQuery.value,
  limit: 10,
});

// Generate preview mutation
const generatePreview = useGenerateOverlayPreview();

// Handle generate preview
const handleGeneratePreview = async () => {
  if (!selectedOverlay.value || !selectedMedia.value) {
    toast.warning('Please select an overlay and a media item');
    return;
  }

  isGenerating.value = true;

  try {
    const result = await generatePreview.mutateAsync({
      overlay_name: selectedOverlay.value,
      media_id: selectedMedia.value,
    });
    previewUrl.value = result.preview_url;
    toast.success('Preview generated');
  } catch (err) {
    toast.error('Failed to generate preview');
  } finally {
    isGenerating.value = false;
  }
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

            <!-- Generate button -->
            <Button
              class="w-full"
              :loading="isGenerating"
              :disabled="!selectedOverlay || !selectedMedia"
              @click="handleGeneratePreview"
            >
              Generate Preview
            </Button>
          </div>
        </Card>

        <!-- Preview -->
        <Card class="flex-1 flex flex-col min-h-0">
          <template #header>
            <span class="font-medium">Preview</span>
          </template>

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
        </Card>
      </div>
    </div>
  </div>
</template>
