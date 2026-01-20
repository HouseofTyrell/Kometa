<script setup lang="ts">
import { ref, computed } from 'vue';
import { usePlaylists, useSavePlaylist, useLibraries } from '@/api';
import { useToast } from '@/composables';
import { Card, Button, Input, Select, Spinner, Badge, Modal } from '@/components/common';

const toast = useToast();

// Fetch playlists and libraries
const { data: playlistsData, isLoading, refetch } = usePlaylists();
const { data: libraries } = useLibraries();
const savePlaylist = useSavePlaylist();

// UI state
const showCreateModal = ref(false);
const selectedFile = ref<string | null>(null);

// Extended builder type with typed config
interface FormBuilder {
  source: string;
  config: {
    list_url?: string;
    any?: string;
    [key: string]: unknown;
  };
}

// New playlist form state
const newPlaylist = ref({
  name: '',
  libraries: [] as string[],
  syncToUsers: 'all',
  builders: [] as FormBuilder[],
});

// Builder sources available for playlists
const builderSources = [
  { value: 'plex_all', label: 'Plex All', description: 'All items from library' },
  { value: 'plex_search', label: 'Plex Search', description: 'Custom Plex search' },
  { value: 'trakt_list', label: 'Trakt List', description: 'Import from Trakt list' },
  { value: 'trakt_watchlist', label: 'Trakt Watchlist', description: 'User Trakt watchlist' },
  { value: 'imdb_list', label: 'IMDb List', description: 'Import from IMDb list' },
  { value: 'tmdb_popular', label: 'TMDb Popular', description: 'Popular movies/shows' },
  { value: 'tmdb_trending', label: 'TMDb Trending', description: 'Currently trending' },
  { value: 'letterboxd_list', label: 'Letterboxd List', description: 'Import from Letterboxd' },
];

// Selected builder source for adding
const selectedBuilderSource = ref('plex_all');

// Library options for multi-select
const libraryOptions = computed(() =>
  libraries.value?.map((l) => ({ value: l.name, label: l.name })) || []
);

// Add a builder to the new playlist
const addBuilder = () => {
  const source = selectedBuilderSource.value;
  const config: FormBuilder['config'] = {};

  // Initialize config with empty strings for fields that need v-model binding
  if (source === 'trakt_list' || source === 'imdb_list' || source === 'letterboxd_list') {
    config.list_url = '';
  } else if (source === 'plex_search') {
    config.any = '';
  }

  newPlaylist.value.builders.push({ source, config });
};

// Remove a builder
const removeBuilder = (index: number) => {
  newPlaylist.value.builders.splice(index, 1);
};

// Reset the form
const resetForm = () => {
  newPlaylist.value = {
    name: '',
    libraries: [],
    syncToUsers: 'all',
    builders: [],
  };
};

// Handle create playlist
const handleCreatePlaylist = async () => {
  if (!newPlaylist.value.name.trim()) {
    toast.warning('Please enter a playlist name');
    return;
  }

  if (newPlaylist.value.builders.length === 0) {
    toast.warning('Please add at least one builder');
    return;
  }

  try {
    await savePlaylist.mutateAsync({
      name: newPlaylist.value.name,
      libraries: newPlaylist.value.libraries.length > 0 ? newPlaylist.value.libraries : undefined,
      sync_to_users: newPlaylist.value.syncToUsers,
      builders: newPlaylist.value.builders,
    });
    toast.success(`Playlist "${newPlaylist.value.name}" configuration saved`);
    showCreateModal.value = false;
    resetForm();
    refetch();
  } catch (err) {
    toast.error('Failed to save playlist');
  }
};

// Get builder label
const getBuilderLabel = (source: string) => {
  return builderSources.find((b) => b.value === source)?.label || source;
};

// Toggle library selection
const toggleLibrary = (libName: string) => {
  const idx = newPlaylist.value.libraries.indexOf(libName);
  if (idx === -1) {
    newPlaylist.value.libraries.push(libName);
  } else {
    newPlaylist.value.libraries.splice(idx, 1);
  }
};
</script>

<template>
  <div class="h-full flex flex-col gap-4">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-xl font-semibold text-content-primary">
          Playlists
        </h2>
        <p class="text-sm text-content-secondary mt-0.5">
          Create and manage Plex playlists across your libraries
        </p>
      </div>
      <Button @click="showCreateModal = true">
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        New Playlist
      </Button>
    </div>

    <!-- Loading -->
    <div v-if="isLoading" class="flex-1 flex items-center justify-center">
      <Spinner size="lg" />
    </div>

    <!-- Content -->
    <div v-else class="flex-1 grid grid-cols-1 lg:grid-cols-3 gap-4 min-h-0 overflow-hidden">
      <!-- Playlist Files List -->
      <Card class="lg:col-span-1 flex flex-col min-h-0" padding="none">
        <template #header>
          <span class="font-medium">Playlist Files</span>
          <Badge variant="default" size="sm">
            {{ playlistsData?.files?.length || 0 }}
          </Badge>
        </template>

        <div v-if="!playlistsData?.files?.length" class="flex-1 flex items-center justify-center p-8 text-content-muted">
          <div class="text-center">
            <svg class="w-12 h-12 mx-auto mb-2 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
            <p>No playlist files configured</p>
            <p class="text-xs mt-1">Create a new playlist to get started</p>
          </div>
        </div>

        <div v-else class="flex-1 overflow-auto p-2 space-y-1">
          <button
            v-for="file in playlistsData.files"
            :key="file.path"
            type="button"
            :class="[
              'w-full flex items-center gap-3 p-3 rounded-lg text-left transition-colors',
              selectedFile === file.path
                ? 'bg-kometa-gold/10 border border-kometa-gold'
                : 'hover:bg-surface-tertiary border border-transparent'
            ]"
            @click="selectedFile = file.path"
          >
            <svg class="w-5 h-5 text-kometa-gold flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
            </svg>
            <div class="flex-1 min-w-0">
              <div class="font-medium text-sm truncate">{{ file.path }}</div>
              <div class="text-xs text-content-muted">
                Library: {{ file.library }}
              </div>
            </div>
          </button>
        </div>
      </Card>

      <!-- Playlist Details / Empty State -->
      <Card class="lg:col-span-2 flex flex-col min-h-0">
        <template #header>
          <span class="font-medium">Playlist Details</span>
        </template>

        <div v-if="!selectedFile" class="flex-1 flex items-center justify-center text-content-muted">
          <div class="text-center">
            <svg class="w-16 h-16 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
            </svg>
            <p class="text-lg font-medium">No playlist selected</p>
            <p class="text-sm mt-1">Select a playlist file to view details</p>
            <p class="text-sm">or create a new playlist</p>
          </div>
        </div>

        <div v-else class="flex-1 overflow-auto">
          <div class="p-4 space-y-4">
            <div class="flex items-center gap-3">
              <Badge variant="info">{{ selectedFile }}</Badge>
            </div>
            <p class="text-sm text-content-muted">
              Playlist file parsing and detailed view coming soon.
              For now, you can edit playlist files directly in the Collections &amp; Overlays Editor.
            </p>
          </div>
        </div>
      </Card>
    </div>

    <!-- Create Playlist Modal -->
    <Modal
      :open="showCreateModal"
      title="Create New Playlist"
      size="lg"
      @close="showCreateModal = false"
    >
      <div class="space-y-6">
        <!-- Playlist Name -->
        <div>
          <label class="block text-sm font-medium text-content-secondary mb-1.5">
            Playlist Name
          </label>
          <Input
            v-model="newPlaylist.name"
            placeholder="My Awesome Playlist"
          />
        </div>

        <!-- Libraries -->
        <div>
          <label class="block text-sm font-medium text-content-secondary mb-1.5">
            Libraries
            <span class="text-content-muted font-normal">(leave empty for all)</span>
          </label>
          <div class="flex flex-wrap gap-2 p-3 bg-surface-tertiary rounded-lg min-h-[44px]">
            <button
              v-for="lib in libraryOptions"
              :key="lib.value"
              type="button"
              :class="[
                'px-3 py-1 rounded-full text-sm transition-colors',
                newPlaylist.libraries.includes(lib.value)
                  ? 'bg-kometa-gold text-black'
                  : 'bg-surface-secondary hover:bg-surface-hover'
              ]"
              @click="toggleLibrary(lib.value)"
            >
              {{ lib.label }}
            </button>
            <span v-if="libraryOptions.length === 0" class="text-content-muted text-sm">
              No libraries available
            </span>
          </div>
        </div>

        <!-- Sync to Users -->
        <div>
          <label class="block text-sm font-medium text-content-secondary mb-1.5">
            Sync to Users
          </label>
          <Select
            v-model="newPlaylist.syncToUsers"
            :options="[
              { value: 'all', label: 'All Users' },
              { value: 'none', label: 'Server Owner Only' },
            ]"
          />
        </div>

        <!-- Builders -->
        <div>
          <label class="block text-sm font-medium text-content-secondary mb-1.5">
            Content Sources (Builders)
          </label>

          <!-- Existing builders -->
          <div v-if="newPlaylist.builders.length > 0" class="space-y-2 mb-3">
            <div
              v-for="(builder, idx) in newPlaylist.builders"
              :key="idx"
              class="flex items-center gap-3 p-3 bg-surface-tertiary rounded-lg"
            >
              <Badge variant="info">{{ getBuilderLabel(builder.source) }}</Badge>
              <div class="flex-1">
                <Input
                  v-if="builder.source === 'trakt_list' || builder.source === 'imdb_list'"
                  :model-value="builder.config.list_url || ''"
                  placeholder="Enter list URL..."
                  class="text-sm"
                  @update:model-value="(v: string | number) => builder.config.list_url = String(v)"
                />
                <Input
                  v-else-if="builder.source === 'plex_search'"
                  :model-value="builder.config.any || ''"
                  placeholder="Search query..."
                  class="text-sm"
                  @update:model-value="(v: string | number) => builder.config.any = String(v)"
                />
                <span v-else class="text-sm text-content-muted">
                  Uses default settings
                </span>
              </div>
              <button
                type="button"
                class="text-red-400 hover:text-red-300 p-1"
                @click="removeBuilder(idx)"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          </div>

          <!-- Add builder -->
          <div class="flex items-center gap-2">
            <Select
              v-model="selectedBuilderSource"
              :options="builderSources.map(b => ({ value: b.value, label: b.label }))"
              class="flex-1"
            />
            <Button variant="secondary" @click="addBuilder">
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              Add
            </Button>
          </div>

          <p v-if="newPlaylist.builders.length === 0" class="text-sm text-content-muted mt-2">
            Add at least one content source to populate the playlist
          </p>
        </div>
      </div>

      <template #footer>
        <div class="flex justify-end gap-3">
          <Button variant="ghost" @click="showCreateModal = false">
            Cancel
          </Button>
          <Button
            :loading="savePlaylist.isPending.value"
            :disabled="!newPlaylist.name || newPlaylist.builders.length === 0"
            @click="handleCreatePlaylist"
          >
            Create Playlist
          </Button>
        </div>
      </template>
    </Modal>
  </div>
</template>
