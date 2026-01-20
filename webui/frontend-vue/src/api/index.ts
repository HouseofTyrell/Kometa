// Export API client
export { api, apiClient, apiRequest } from './client';

// Export config API
export {
  configKeys,
  useConfig,
  useValidateConfig,
  useConfigBackups,
  useLibraries,
  useSaveConfig,
  useCreateBackup,
  useRestoreBackup,
  useDeleteBackup,
} from './config';

// Export run API
export {
  runKeys,
  useRunHistory,
  useRunDetail,
  useRunStatus,
  useRunLogs,
  useRunDiff,
  useStartRun,
  useStartApplyRun,
  useStopRun,
  useDeleteRun,
  type DryRunDiffResponse,
} from './run';

// Export media API
export {
  mediaKeys,
  overlayKeys,
  connectionKeys,
  useMediaSearch,
  useMediaItem,
  useOverlayList,
  useGenerateOverlayPreview,
  useTestConnection,
  useTestAllConnections,
  useSettings,
  useUpdateSettings,
  type TestConnectionParams,
} from './media';

// Export collections API
export {
  collectionKeys,
  useCollectionFiles,
  useCollectionFile,
  useSaveCollectionFile,
} from './collections';

// Export scheduler API
export {
  schedulerKeys,
  useSchedulerStatus,
  useConfigureScheduler,
  useStopScheduler,
  type SchedulerStatus,
} from './scheduler';

// Export playlists API
export {
  playlistKeys,
  usePlaylists,
  useSavePlaylist,
  type PlaylistFile,
  type PlaylistBuilder,
  type PlaylistDefinition,
  type SavePlaylistParams,
} from './playlists';

// Export metadata API
export {
  metadataKeys,
  useMetadataBrowse,
  useMetadataItem,
  useGenerateMetadataYaml,
  type MetadataBrowseParams,
  type MetadataItem,
  type MetadataBrowseResponse,
  type MetadataItemDetail,
} from './metadata';
