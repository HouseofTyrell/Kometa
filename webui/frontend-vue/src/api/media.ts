import { useQuery, useMutation } from '@tanstack/vue-query';
import { computed, type MaybeRefOrGetter, toValue } from 'vue';
import { api } from './client';
import type { MediaItem, MediaSearchParams, OverlayPreview, ConnectionTest } from '@/types';

// Query keys
export const mediaKeys = {
  all: ['media'] as const,
  search: (params: MediaSearchParams) => [...mediaKeys.all, 'search', params] as const,
  item: (id: string) => [...mediaKeys.all, 'item', id] as const,
};

export const overlayKeys = {
  all: ['overlays'] as const,
  list: () => [...overlayKeys.all, 'list'] as const,
  preview: (name: string) => [...overlayKeys.all, 'preview', name] as const,
};

export const connectionKeys = {
  all: ['connections'] as const,
  test: (service: string) => [...connectionKeys.all, 'test', service] as const,
};

// Types
interface MediaSearchResponse {
  results: MediaItem[];
  source: string;
  query: string;
}

// Frontend-friendly response format
interface MediaSearchResult {
  items: MediaItem[];
  total: number;
  error?: string;  // Optional error message if search failed
}

// Backend overlay list response format
interface BackendOverlayListResponse {
  default: Array<{ name: string; path: string; type: string }>;
  custom: Array<{ name: string; path: string; type: string }>;
}

// Frontend-friendly overlay list response
interface OverlayListResponse {
  overlays: string[];
}

// Media Queries

// Backend media item format
interface BackendMediaItem {
  rating_key: string;
  title: string;
  year?: string;
  type: string;
  library?: string;
  thumb?: string;
  thumb_url?: string;
  art?: string;
  summary?: string;
}

/**
 * Search for media items
 * Accepts reactive params (ref, computed, or getter function)
 */
export function useMediaSearch(params: MaybeRefOrGetter<MediaSearchParams>) {
  return useQuery({
    queryKey: computed(() => mediaKeys.search(toValue(params))),
    queryFn: async () => {
      const p = toValue(params);
      const response = await api.get<{ results: BackendMediaItem[]; source: string; query: string; error?: string }>('/media/search', {
        params: {
          query: p.query,
          library: p.library,
          source: 'plex',
          media_type: p.type || 'movie',
          limit: p.limit || 20,
        },
      });

      // If there's an error from the backend (e.g., Plex not configured), return it
      if (response.error) {
        return {
          items: [],
          total: 0,
          error: response.error,
        } as MediaSearchResult;
      }

      // Transform backend response to frontend format
      const items: MediaItem[] = (response.results || []).map((item) => ({
        id: item.rating_key,
        title: item.title,
        year: item.year ? parseInt(item.year, 10) : undefined,
        type: item.type as MediaItem['type'],
        poster_url: item.thumb_url,
        summary: item.summary,
      }));
      return {
        items,
        total: items.length,
      } as MediaSearchResult;
    },
    enabled: computed(() => {
      const p = toValue(params);
      return !!p.query && p.query.length >= 2;
    }),
  });
}

/**
 * Get media item details
 */
export function useMediaItem(id: string) {
  return useQuery({
    queryKey: mediaKeys.item(id),
    queryFn: () => api.get<MediaItem>(`/media/${id}`),
    enabled: !!id,
  });
}

// Overlay Queries

/**
 * Get list of available overlays
 */
export function useOverlayList() {
  return useQuery({
    queryKey: overlayKeys.list(),
    queryFn: async () => {
      const response = await api.get<BackendOverlayListResponse>('/overlays');
      // Transform backend response to frontend format
      // Flatten default and custom overlays into a single array of names
      const overlayNames: string[] = [];

      // Add default overlays
      if (response.default && Array.isArray(response.default)) {
        for (const overlay of response.default) {
          overlayNames.push(overlay.name);
        }
      }

      // Add custom overlays (prefixed with "custom/" to distinguish)
      if (response.custom && Array.isArray(response.custom)) {
        for (const overlay of response.custom) {
          overlayNames.push(`custom/${overlay.name}`);
        }
      }

      return { overlays: overlayNames } as OverlayListResponse;
    },
  });
}

/**
 * Generate overlay preview for a single overlay
 * Uses the simplified endpoint that takes overlay name and media ID
 */
export function useGenerateOverlayPreview() {
  return useMutation({
    mutationFn: (params: {
      overlay_name: string;
      media_id: string;
      poster_source?: 'tmdb' | 'plex';  // tmdb = clean poster, plex = current poster
      library?: string;  // Library name to get overlay config from (uses template_variables from config)
      settings?: Record<string, unknown>;
      config_content?: string;  // Optional YAML config content (uses current editor config instead of disk)
    }) => api.post<OverlayPreview>('/overlays/preview/simple', params),
  });
}

/**
 * Generate overlay preview from config
 * Uses all overlays configured for a library in the config's overlay_files section
 */
export function useGenerateConfigOverlayPreview() {
  return useMutation({
    mutationFn: (params: {
      media_id: string;
      library: string;  // Library name to get overlay_files from
      poster_source?: 'tmdb' | 'plex';  // tmdb = clean poster, plex = current poster
      config_content?: string;  // Optional YAML config content (uses current editor config instead of disk)
    }) => api.post<OverlayPreview>('/overlays/preview/from-config', params),
  });
}

// Connection Testing

/**
 * All testable services
 */
export type TestableService =
  | 'plex'
  | 'tmdb'
  | 'radarr'
  | 'sonarr'
  | 'tautulli'
  | 'trakt'
  | 'mdblist'
  | 'omdb'
  | 'mal'
  | 'anidb'
  | 'github'
  | 'notifiarr'
  | 'gotify'
  | 'ntfy';

/**
 * Test connection request parameters for each service
 */
export interface TestConnectionParams {
  service: TestableService;
  config: Record<string, unknown>;
}

/**
 * Test a service connection
 */
export function useTestConnection() {
  return useMutation({
    mutationFn: ({ service, config }: TestConnectionParams) => {
      // Map config to the expected request format for each service
      let body: Record<string, unknown> = {};

      switch (service) {
        case 'plex':
          body = {
            url: config.url,
            token: config.token,
          };
          break;
        case 'tmdb':
        case 'mdblist':
        case 'omdb':
        case 'notifiarr':
          body = {
            apikey: config.apikey,
          };
          break;
        case 'radarr':
        case 'sonarr':
          body = {
            url: config.url,
            token: config.token,
          };
          break;
        case 'tautulli':
          body = {
            url: config.url,
            apikey: config.apikey,
          };
          break;
        case 'trakt':
          body = {
            client_id: config.client_id,
            client_secret: config.client_secret,
          };
          break;
        case 'mal':
          body = {
            client_id: config.client_id,
            client_secret: config.client_secret,
          };
          break;
        case 'anidb':
          body = {
            username: config.username,
            password: config.password,
          };
          break;
        case 'github':
          body = {
            token: config.token,
          };
          break;
        case 'gotify':
          body = {
            url: config.url,
            token: config.token,
          };
          break;
        case 'ntfy':
          body = {
            url: config.url || 'https://ntfy.sh',
            topic: config.topic,
          };
          break;
      }

      return api.post<ConnectionTest>(`/test/${service}`, body);
    },
  });
}

/**
 * Test all connections
 */
export function useTestAllConnections() {
  return useMutation({
    mutationFn: () => api.post<ConnectionTest[]>('/test/all'),
  });
}

// Settings

/**
 * Get current settings (apply mode, password requirement, etc.)
 */
export function useSettings() {
  return useQuery({
    queryKey: ['settings'],
    queryFn: () =>
      api.get<{
        apply_enabled: boolean;
        password_required: boolean;
        version: string;
      }>('/settings'),
  });
}

/**
 * Update settings
 */
export function useUpdateSettings() {
  return useMutation({
    mutationFn: (settings: { apply_enabled?: boolean; password?: string }) =>
      api.put<{ success: boolean }>('/settings', settings),
  });
}

// Webhook Testing

export interface WebhookTestParams {
  url: string;
  event?: string;
  service?: 'discord' | 'slack' | 'teams' | 'custom';
}

export interface WebhookTestResponse {
  success: boolean;
  message?: string;
  error?: string;
}

/**
 * Test a webhook by sending a test notification
 */
export function useTestWebhook() {
  return useMutation({
    mutationFn: (params: WebhookTestParams) =>
      api.post<WebhookTestResponse>('/webhooks/test', {
        url: params.url,
        event: params.event || 'test',
        service: params.service || 'custom',
      }),
  });
}
