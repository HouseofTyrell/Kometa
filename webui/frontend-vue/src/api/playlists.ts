/**
 * Playlist API hooks
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query';
import { api } from './client';

// Query keys
export const playlistKeys = {
  all: ['playlists'] as const,
  list: () => [...playlistKeys.all, 'list'] as const,
  files: () => [...playlistKeys.all, 'files'] as const,
};

// Types
export interface PlaylistFile {
  library: string;
  path: string;
  file_path: string;
}

export interface PlaylistBuilder {
  source: string;
  config: Record<string, unknown>;
}

export interface PlaylistDefinition {
  name: string;
  libraries?: string[];
  sync_to_users?: string[] | 'all';
  builders: PlaylistBuilder[];
  filters?: Record<string, unknown>;
  schedule?: string;
}

export interface PlaylistsResponse {
  playlists: PlaylistDefinition[];
  files: PlaylistFile[];
}

export interface SavePlaylistParams {
  name: string;
  libraries?: string[];
  sync_to_users?: string;
  builders: PlaylistBuilder[];
  filters?: Record<string, unknown>;
}

export interface SavePlaylistResponse {
  success: boolean;
  message: string;
  config: Record<string, unknown>;
}

/**
 * Get all playlists and playlist files
 */
export function usePlaylists() {
  return useQuery({
    queryKey: playlistKeys.list(),
    queryFn: async () => {
      const response = await api.get<PlaylistsResponse>('/playlists');
      return response;
    },
  });
}

/**
 * Save a playlist definition
 */
export function useSavePlaylist() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (params: SavePlaylistParams) => {
      const response = await api.post<SavePlaylistResponse>('/playlists/save', params);
      return response;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: playlistKeys.all });
    },
  });
}
