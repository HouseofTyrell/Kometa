/**
 * Metadata Browser API hooks
 */

import { useQuery, useMutation } from '@tanstack/vue-query';
import { computed, type Ref } from 'vue';
import { api } from './client';

// Query keys
export const metadataKeys = {
  all: ['metadata'] as const,
  browse: (library: string, params: MetadataBrowseParams) =>
    [...metadataKeys.all, 'browse', library, params] as const,
  item: (id: string) => [...metadataKeys.all, 'item', id] as const,
};

// Types
export interface MetadataBrowseParams {
  page?: number;
  per_page?: number;
  search?: string;
  type?: 'all' | 'movie' | 'show';
  sort?: 'title' | 'added' | 'year' | 'rating';
}

export interface MetadataItem {
  id: string;
  title: string;
  year?: number;
  type: 'movie' | 'show' | 'episode' | 'season';
  thumb?: string;
  rating?: number;
  summary?: string;
  studio?: string;
  genres?: string[];
  added_at?: string;
  updated_at?: string;
  content_rating?: string;
  duration?: number;
  season_count?: number;
  episode_count?: number;
}

export interface MetadataBrowseResponse {
  items: MetadataItem[];
  total: number;
  page: number;
  total_pages: number;
  library: string;
  error?: string;
}

export interface MetadataItemDetail extends MetadataItem {
  // Extended details
  originally_available?: string;
  audience_rating?: number;
  tagline?: string;
  directors?: string[];
  writers?: string[];
  actors?: Array<{ name: string; role?: string; thumb?: string }>;
  collections?: string[];
  labels?: string[];
  guid?: string;
  key?: string;
}

export interface GenerateYamlParams {
  items: Array<{
    title: string;
    year?: number;
    [key: string]: unknown;
  }>;
}

export interface GenerateYamlResponse {
  yaml: string;
  item_count: number;
}

/**
 * Browse metadata for a library with pagination
 */
export function useMetadataBrowse(
  library: Ref<string>,
  params: Ref<MetadataBrowseParams>
) {
  return useQuery({
    queryKey: computed(() => metadataKeys.browse(library.value, params.value)),
    queryFn: async () => {
      const queryParams = new URLSearchParams();
      if (params.value.page) queryParams.set('page', String(params.value.page));
      if (params.value.per_page) queryParams.set('per_page', String(params.value.per_page));
      if (params.value.search) queryParams.set('search', params.value.search);
      if (params.value.type && params.value.type !== 'all') queryParams.set('type', params.value.type);
      if (params.value.sort) queryParams.set('sort', params.value.sort);

      const url = `/metadata/browse/${encodeURIComponent(library.value)}${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
      const response = await api.get<MetadataBrowseResponse>(url);
      return response;
    },
    enabled: computed(() => !!library.value),
  });
}

/**
 * Get detailed metadata for a specific item
 */
export function useMetadataItem(itemId: Ref<string | null>) {
  return useQuery({
    queryKey: computed(() => metadataKeys.item(itemId.value || '')),
    queryFn: async () => {
      if (!itemId.value) throw new Error('No item ID');
      const response = await api.get<MetadataItemDetail>(`/metadata/item/${itemId.value}`);
      return response;
    },
    enabled: computed(() => !!itemId.value),
  });
}

/**
 * Generate Kometa metadata YAML
 */
export function useGenerateMetadataYaml() {
  return useMutation({
    mutationFn: async (params: GenerateYamlParams) => {
      const response = await api.post<GenerateYamlResponse>('/metadata/generate-yaml', params.items);
      return response;
    },
  });
}
