<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useLibraries } from '@/api';
import { useMetadataBrowse, useMetadataItem } from '@/api/metadata';
import { Card, Button, Input, Select, Spinner, Badge, Modal } from '@/components/common';
import type { MetadataBrowseParams, MetadataItem } from '@/api/metadata';

// Libraries for selection
const { data: libraries, isLoading: librariesLoading } = useLibraries();

// Browse state
const selectedLibrary = ref('');
const searchQuery = ref('');
const filterType = ref<'all' | 'movie' | 'show'>('all');
const sortBy = ref<'title' | 'added' | 'year' | 'rating'>('title');
const currentPage = ref(1);
const perPage = ref(24);

// Debounced search
const debouncedSearch = ref('');
let searchDebounce: ReturnType<typeof setTimeout>;
watch(searchQuery, (val) => {
  clearTimeout(searchDebounce);
  searchDebounce = setTimeout(() => {
    debouncedSearch.value = val;
    currentPage.value = 1;
  }, 300);
});

// Browse params
const browseParams = computed<MetadataBrowseParams>(() => ({
  page: currentPage.value,
  per_page: perPage.value,
  search: debouncedSearch.value || undefined,
  type: filterType.value,
  sort: sortBy.value,
}));

// Metadata browse query
const {
  data: browseData,
  isLoading: browseLoading,
  isFetching: browseFetching,
} = useMetadataBrowse(selectedLibrary, browseParams);

// Selected item for detail view
const selectedItemId = ref<string | null>(null);
const showDetailModal = ref(false);

// Item detail query
const { data: itemDetail, isLoading: detailLoading } = useMetadataItem(selectedItemId);

// Library options
const libraryOptions = computed(() => [
  { value: '', label: 'Select a library...' },
  ...(libraries.value?.map((l) => ({ value: l.name, label: l.name })) || []),
]);

// Type filter options
const typeOptions = [
  { value: 'all', label: 'All Types' },
  { value: 'movie', label: 'Movies' },
  { value: 'show', label: 'TV Shows' },
];

// Sort options
const sortOptions = [
  { value: 'title', label: 'Title' },
  { value: 'added', label: 'Recently Added' },
  { value: 'year', label: 'Release Year' },
  { value: 'rating', label: 'Rating' },
];

// Open item detail
const openDetail = (item: MetadataItem) => {
  selectedItemId.value = item.id;
  showDetailModal.value = true;
};

// Close detail
const closeDetail = () => {
  showDetailModal.value = false;
  selectedItemId.value = null;
};

// Format duration
const formatDuration = (ms?: number) => {
  if (!ms) return '';
  const minutes = Math.floor(ms / 60000);
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  return hours > 0 ? `${hours}h ${mins}m` : `${mins}m`;
};

// Placeholder image
const placeholderImage =
  'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 450"><rect fill="%232a2a4e" width="300" height="450"/><text x="150" y="225" text-anchor="middle" fill="%23666" font-size="24">No Poster</text></svg>';

// Pagination
const totalPages = computed(() => browseData.value?.total_pages || 0);
const canPrevPage = computed(() => currentPage.value > 1);
const canNextPage = computed(() => currentPage.value < totalPages.value);

const prevPage = () => {
  if (canPrevPage.value) currentPage.value--;
};

const nextPage = () => {
  if (canNextPage.value) currentPage.value++;
};

// Reset page when library changes
watch(selectedLibrary, () => {
  currentPage.value = 1;
});
</script>

<template>
  <div class="h-full flex flex-col gap-4">
    <!-- Header -->
    <div>
      <h2 class="text-xl font-semibold text-content-primary">
        Metadata Browser
      </h2>
      <p class="text-sm text-content-secondary mt-0.5">
        Browse and view metadata for items in your Plex libraries
      </p>
    </div>

    <!-- Library Selection & Filters -->
    <div class="flex items-center gap-4 flex-wrap">
      <div class="w-64">
        <Select
          v-model="selectedLibrary"
          :options="libraryOptions"
          :disabled="librariesLoading"
        />
      </div>

      <div class="flex-1 min-w-[200px]">
        <Input
          v-model="searchQuery"
          type="search"
          placeholder="Search items..."
          :disabled="!selectedLibrary"
        />
      </div>

      <div class="w-40">
        <Select
          v-model="filterType"
          :options="typeOptions"
          :disabled="!selectedLibrary"
        />
      </div>

      <div class="w-44">
        <Select
          v-model="sortBy"
          :options="sortOptions"
          :disabled="!selectedLibrary"
        />
      </div>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-auto">
      <!-- No library selected -->
      <div
        v-if="!selectedLibrary"
        class="flex flex-col items-center justify-center h-full text-content-muted"
      >
        <svg class="w-16 h-16 mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
        </svg>
        <p class="text-lg font-medium">Select a Library</p>
        <p class="text-sm mt-1">Choose a library to browse its metadata</p>
      </div>

      <!-- Loading -->
      <div
        v-else-if="browseLoading && !browseData"
        class="flex items-center justify-center h-full"
      >
        <Spinner size="lg" />
      </div>

      <!-- Error -->
      <div
        v-else-if="browseData?.error"
        class="flex flex-col items-center justify-center h-full text-content-muted"
      >
        <svg class="w-16 h-16 mb-4 text-red-400 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <p class="text-lg font-medium text-red-400">Error loading metadata</p>
        <p class="text-sm mt-1">{{ browseData.error }}</p>
      </div>

      <!-- No results -->
      <div
        v-else-if="browseData?.items?.length === 0"
        class="flex flex-col items-center justify-center h-full text-content-muted"
      >
        <svg class="w-16 h-16 mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p class="text-lg font-medium">No items found</p>
        <p v-if="debouncedSearch" class="text-sm mt-1">
          No results for "{{ debouncedSearch }}"
        </p>
      </div>

      <!-- Results grid -->
      <div v-else>
        <!-- Loading overlay -->
        <div
          v-if="browseFetching"
          class="absolute inset-0 bg-surface-primary/50 flex items-center justify-center z-10"
        >
          <Spinner size="lg" />
        </div>

        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8 gap-4">
          <Card
            v-for="item in browseData?.items"
            :key="item.id"
            class="overflow-hidden cursor-pointer hover:ring-2 hover:ring-kometa-gold transition-all"
            padding="none"
            hoverable
            @click="openDetail(item)"
          >
            <!-- Poster -->
            <div class="aspect-[2/3] bg-surface-tertiary relative">
              <img
                :src="item.thumb || placeholderImage"
                :alt="item.title"
                class="w-full h-full object-cover"
                loading="lazy"
              >
              <!-- Type badge -->
              <Badge
                :variant="item.type === 'movie' ? 'info' : 'success'"
                size="sm"
                class="absolute top-1 right-1"
              >
                {{ item.type }}
              </Badge>
            </div>

            <!-- Info -->
            <div class="p-2">
              <h3 class="font-medium text-sm truncate" :title="item.title">
                {{ item.title }}
              </h3>
              <div class="flex items-center gap-2 mt-1">
                <span v-if="item.year" class="text-xs text-content-muted">
                  {{ item.year }}
                </span>
                <div v-if="item.rating" class="flex items-center gap-1">
                  <svg class="w-3 h-3 text-kometa-gold" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
                  </svg>
                  <span class="text-xs text-content-secondary">{{ item.rating.toFixed(1) }}</span>
                </div>
              </div>
            </div>
          </Card>
        </div>

        <!-- Pagination -->
        <div
          v-if="totalPages > 1"
          class="flex items-center justify-center gap-4 mt-6 py-4"
        >
          <Button
            variant="secondary"
            size="sm"
            :disabled="!canPrevPage"
            @click="prevPage"
          >
            <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
            Previous
          </Button>

          <span class="text-sm text-content-muted">
            Page {{ currentPage }} of {{ totalPages }}
            <span class="text-content-secondary ml-2">({{ browseData?.total }} items)</span>
          </span>

          <Button
            variant="secondary"
            size="sm"
            :disabled="!canNextPage"
            @click="nextPage"
          >
            Next
            <svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </Button>
        </div>
      </div>
    </div>

    <!-- Item Detail Modal -->
    <Modal
      :open="showDetailModal"
      :title="itemDetail?.title || 'Loading...'"
      size="xl"
      @close="closeDetail"
    >
      <div v-if="detailLoading" class="flex items-center justify-center py-12">
        <Spinner size="lg" />
      </div>

      <div v-else-if="itemDetail" class="flex gap-6">
        <!-- Poster -->
        <div class="w-48 flex-shrink-0">
          <img
            :src="itemDetail.thumb || placeholderImage"
            :alt="itemDetail.title"
            class="w-full rounded-lg shadow-lg"
          >
        </div>

        <!-- Details -->
        <div class="flex-1 space-y-4">
          <!-- Title & Year -->
          <div>
            <h3 class="text-xl font-semibold">{{ itemDetail.title }}</h3>
            <div class="flex items-center gap-3 mt-1 text-sm text-content-muted">
              <span v-if="itemDetail.year">{{ itemDetail.year }}</span>
              <Badge :variant="itemDetail.type === 'movie' ? 'info' : 'success'">
                {{ itemDetail.type }}
              </Badge>
              <span v-if="itemDetail.content_rating">{{ itemDetail.content_rating }}</span>
              <span v-if="itemDetail.duration">{{ formatDuration(itemDetail.duration) }}</span>
            </div>
          </div>

          <!-- Rating -->
          <div v-if="itemDetail.rating" class="flex items-center gap-2">
            <svg class="w-5 h-5 text-kometa-gold" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
            </svg>
            <span class="font-medium">{{ itemDetail.rating.toFixed(1) }}</span>
            <span class="text-content-muted">/ 10</span>
          </div>

          <!-- Summary -->
          <div v-if="itemDetail.summary">
            <h4 class="text-sm font-medium text-content-secondary mb-1">Summary</h4>
            <p class="text-sm text-content-muted leading-relaxed">{{ itemDetail.summary }}</p>
          </div>

          <!-- Genres -->
          <div v-if="itemDetail.genres?.length">
            <h4 class="text-sm font-medium text-content-secondary mb-1">Genres</h4>
            <div class="flex flex-wrap gap-1">
              <Badge
                v-for="genre in itemDetail.genres"
                :key="genre"
                variant="default"
                size="sm"
              >
                {{ genre }}
              </Badge>
            </div>
          </div>

          <!-- Studio -->
          <div v-if="itemDetail.studio">
            <h4 class="text-sm font-medium text-content-secondary mb-1">Studio</h4>
            <p class="text-sm text-content-muted">{{ itemDetail.studio }}</p>
          </div>

          <!-- TV Show info -->
          <div v-if="itemDetail.type === 'show'" class="flex gap-4">
            <div v-if="itemDetail.season_count">
              <h4 class="text-sm font-medium text-content-secondary">Seasons</h4>
              <p class="text-lg font-semibold">{{ itemDetail.season_count }}</p>
            </div>
            <div v-if="itemDetail.episode_count">
              <h4 class="text-sm font-medium text-content-secondary">Episodes</h4>
              <p class="text-lg font-semibold">{{ itemDetail.episode_count }}</p>
            </div>
          </div>

          <!-- Metadata ID -->
          <div v-if="itemDetail.guid" class="pt-2 border-t border-border">
            <h4 class="text-sm font-medium text-content-secondary mb-1">Plex GUID</h4>
            <code class="text-xs text-content-muted bg-surface-tertiary px-2 py-1 rounded">
              {{ itemDetail.guid }}
            </code>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="flex justify-between items-center w-full">
          <p class="text-xs text-content-muted">
            To edit metadata, use Kometa metadata files or edit in Plex directly.
          </p>
          <Button variant="secondary" @click="closeDetail">
            Close
          </Button>
        </div>
      </template>
    </Modal>
  </div>
</template>
