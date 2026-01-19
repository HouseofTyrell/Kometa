/**
 * Collection & Overlay file API hooks
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query';
import { api } from './client';

// Query keys
export const collectionKeys = {
  all: ['collections'] as const,
  files: () => [...collectionKeys.all, 'files'] as const,
  file: (filename: string) => [...collectionKeys.all, 'file', filename] as const,
};

// Types
interface CollectionFile {
  name: string;
  path: string;
  type: 'collection' | 'overlay';
  size: number;
  modified: string;
}

interface CollectionFileContent {
  exists: boolean;
  filename: string;
  path?: string;
  content: string;
}

interface SaveCollectionFileParams {
  filename: string;
  content: string;
  file_type: 'collection' | 'overlay';
}

interface SaveCollectionFileResponse {
  success: boolean;
  message: string;
  path: string;
}

/**
 * List all collection and overlay files
 */
export function useCollectionFiles() {
  return useQuery({
    queryKey: collectionKeys.files(),
    queryFn: async () => {
      const response = await api.get<{ files: CollectionFile[] }>('/collections/files');
      return response.files;
    },
  });
}

/**
 * Load a specific collection/overlay file
 */
export function useCollectionFile(filename: string) {
  return useQuery({
    queryKey: collectionKeys.file(filename),
    queryFn: async () => {
      const response = await api.get<CollectionFileContent>(`/collections/file/${encodeURIComponent(filename)}`);
      return response;
    },
    enabled: !!filename,
  });
}

/**
 * Save a collection/overlay file
 */
export function useSaveCollectionFile() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (params: SaveCollectionFileParams) => {
      const response = await api.post<SaveCollectionFileResponse>('/collections/file/save', params);
      return response;
    },
    onSuccess: (_, variables) => {
      // Invalidate the files list and the specific file
      queryClient.invalidateQueries({ queryKey: collectionKeys.files() });
      queryClient.invalidateQueries({ queryKey: collectionKeys.file(variables.filename) });
    },
  });
}
