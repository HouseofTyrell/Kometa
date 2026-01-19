<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
import { useConfigStore } from '@/stores';
import { useConfig, useSaveConfig, useValidateConfig, useCreateBackup, useConfigBackups, useRestoreBackup, useTestConnection } from '@/api';
import { useToast, useConfirm } from '@/composables';
import { Card, Button, Badge, Spinner, Modal } from '@/components/common';
import { ConfigEditor, ValidationPanel } from '@/components/config';

const config = useConfigStore();
const toast = useToast();
const { confirmWarning } = useConfirm();

// Fetch config
const { data: configData, isLoading, error, refetch } = useConfig();

// Mutations
const saveConfigMutation = useSaveConfig();
const validateMutation = useValidateConfig();
const createBackupMutation = useCreateBackup();
const restoreBackupMutation = useRestoreBackup();
const testConnectionMutation = useTestConnection();

// Backups
const { data: backups, refetch: refetchBackups } = useConfigBackups();
const showBackupsModal = ref(false);

// Validation panel
const showValidation = ref(true);

// File input ref
const fileInputRef = ref<HTMLInputElement | null>(null);

// Editor state
const editorContent = ref('');
const originalContent = ref('');
const hasLocalChanges = computed(() => editorContent.value !== originalContent.value);

// Undo/Redo history
const undoStack = ref<string[]>([]);
const redoStack = ref<string[]>([]);
const isUndoRedo = ref(false);
const MAX_HISTORY = 50;

const canUndo = computed(() => undoStack.value.length > 0);
const canRedo = computed(() => redoStack.value.length > 0);

function pushToHistory(content: string) {
  if (isUndoRedo.value) return;

  // Don't push if it's the same as the last item
  if (undoStack.value.length > 0 && undoStack.value[undoStack.value.length - 1] === content) {
    return;
  }

  undoStack.value.push(content);

  // Limit history size
  if (undoStack.value.length > MAX_HISTORY) {
    undoStack.value.shift();
  }

  // Clear redo stack when new changes are made
  redoStack.value = [];
}

function handleUndo() {
  if (!canUndo.value) return;

  isUndoRedo.value = true;

  // Push current state to redo stack
  redoStack.value.push(editorContent.value);

  // Pop from undo stack and apply
  const previousState = undoStack.value.pop()!;
  editorContent.value = previousState;

  isUndoRedo.value = false;
}

function handleRedo() {
  if (!canRedo.value) return;

  isUndoRedo.value = true;

  // Push current state to undo stack
  undoStack.value.push(editorContent.value);

  // Pop from redo stack and apply
  const nextState = redoStack.value.pop()!;
  editorContent.value = nextState;

  isUndoRedo.value = false;
}

// Keyboard shortcuts for undo/redo
function handleKeyDown(e: KeyboardEvent) {
  const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
  const modKey = isMac ? e.metaKey : e.ctrlKey;

  if (modKey && e.key === 'z' && !e.shiftKey) {
    e.preventDefault();
    handleUndo();
  } else if (modKey && e.key === 'z' && e.shiftKey) {
    e.preventDefault();
    handleRedo();
  } else if (modKey && e.key === 'y') {
    e.preventDefault();
    handleRedo();
  } else if (modKey && e.key === 's') {
    e.preventDefault();
    if (hasLocalChanges.value && config.isValid) {
      handleSave();
    }
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeyDown);
});

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown);
});

// Watch for config data changes
watch(
  () => configData.value?.content,
  (newContent) => {
    if (newContent !== undefined) {
      // Only update if we haven't made local changes yet
      // or if this is a fresh load (originalContent matches editorContent)
      if (editorContent.value === originalContent.value) {
        editorContent.value = newContent;
        originalContent.value = newContent;
        config.setRawConfig(newContent, false);
      }
    }
  },
  { immediate: true }
);

// Validate on change (debounced) and track history
let validateTimeout: ReturnType<typeof setTimeout>;
let historyTimeout: ReturnType<typeof setTimeout>;
let lastHistoryContent = '';

watch(editorContent, (content, oldContent) => {
  config.setRawConfig(content);

  // Push to history after a delay (batch rapid changes)
  if (!isUndoRedo.value && oldContent && oldContent !== content) {
    clearTimeout(historyTimeout);
    historyTimeout = setTimeout(() => {
      if (lastHistoryContent !== oldContent) {
        pushToHistory(oldContent);
        lastHistoryContent = oldContent;
      }
    }, 500);
  }

  clearTimeout(validateTimeout);
  validateTimeout = setTimeout(async () => {
    try {
      const result = await validateMutation.mutateAsync(content);
      config.setValidation(result);
    } catch (err) {
      // Validation error handling
    }
  }, 500);
});

// Save config
const handleSave = async () => {
  if (!config.isValid) {
    toast.error('Cannot save: Configuration has validation errors');
    return;
  }

  try {
    await saveConfigMutation.mutateAsync(editorContent.value);
    originalContent.value = editorContent.value; // Reset change tracking
    config.markSaved();
    toast.success('Configuration saved successfully');
  } catch (err) {
    toast.error('Failed to save configuration');
  }
};

// Create backup
const handleBackup = async () => {
  try {
    const result = await createBackupMutation.mutateAsync();
    refetchBackups();
    toast.success(`Backup created: ${result.filename}`);
  } catch (err) {
    toast.error('Failed to create backup');
  }
};

// Discard changes
const handleDiscard = async () => {
  if (!hasLocalChanges.value) return;

  const confirmed = await confirmWarning(
    'Discard Changes?',
    'Are you sure you want to discard all unsaved changes? This cannot be undone.'
  );

  if (confirmed) {
    editorContent.value = originalContent.value;
    config.setRawConfig(editorContent.value, false);
    toast.info('Changes discarded');
  }
};

// Format timestamp
const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleString();
};

// Format file size
const formatSize = (bytes: number) => {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
};

// Upload config file
const handleUpload = () => {
  fileInputRef.value?.click();
};

const handleFileChange = async (event: Event) => {
  const input = event.target as HTMLInputElement;
  const file = input.files?.[0];

  if (!file) return;

  // Validate file type
  if (!file.name.endsWith('.yml') && !file.name.endsWith('.yaml')) {
    toast.error('Please select a YAML file (.yml or .yaml)');
    input.value = '';
    return;
  }

  // Check if there are unsaved changes
  if (hasLocalChanges.value) {
    const confirmed = await confirmWarning(
      'Unsaved Changes',
      'You have unsaved changes. Uploading a new file will replace the current content. Continue?'
    );
    if (!confirmed) {
      input.value = '';
      return;
    }
  }

  const reader = new FileReader();
  reader.onload = (e) => {
    const content = e.target?.result as string;
    editorContent.value = content;
    config.setRawConfig(content);
    toast.success(`Loaded config from ${file.name}`);
  };
  reader.onerror = () => {
    toast.error('Failed to read the uploaded file');
  };
  reader.readAsText(file);

  // Reset input for reuse
  input.value = '';
};

// Download config file
const handleDownload = () => {
  const content = editorContent.value;
  if (!content) {
    toast.error('No configuration to download');
    return;
  }

  const blob = new Blob([content], { type: 'text/yaml' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'config.yml';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  toast.success('Configuration downloaded');
};

// Restore backup
const handleRestore = async (filename: string) => {
  const confirmed = await confirmWarning(
    'Restore Backup?',
    `Are you sure you want to restore from ${filename}? This will replace the current configuration.`
  );

  if (!confirmed) return;

  try {
    await restoreBackupMutation.mutateAsync(filename);
    const result = await refetch();
    // Update both editor and original content with restored content
    if (result.data?.content) {
      editorContent.value = result.data.content;
      originalContent.value = result.data.content;
      config.setRawConfig(result.data.content, false);
    }
    showBackupsModal.value = false;
    toast.success('Backup restored successfully');
  } catch (err) {
    toast.error('Failed to restore backup');
  }
};

// Test connection
const handleTestConnection = async (service: string, config: Record<string, unknown>) => {
  try {
    const result = await testConnectionMutation.mutateAsync({
      service: service as 'plex' | 'tmdb' | 'radarr' | 'sonarr' | 'tautulli' | 'trakt' | 'notifiarr',
      config,
    });
    if (result.success) {
      toast.success(`${service} connection successful`);
    } else {
      toast.error(`${service} connection failed: ${result.error || result.message}`);
    }
  } catch (err) {
    toast.error(`Failed to test ${service} connection`);
  }
};
</script>

<template>
  <div class="h-full flex flex-col">
    <!-- Header -->
    <div class="flex items-center justify-between p-4 border-b border-border">
      <div>
        <h2 class="text-xl font-semibold text-content-primary">
          Configuration
        </h2>
        <p class="text-sm text-content-secondary mt-0.5">
          Edit your Kometa configuration file
        </p>
      </div>

      <div class="flex items-center gap-2">
        <!-- Validation status -->
        <Badge
          v-if="config.hasErrors"
          variant="error"
        >
          {{ config.validation.errors.length }} error(s)
        </Badge>
        <Badge
          v-else-if="config.hasWarnings"
          variant="warning"
        >
          {{ config.validation.warnings.length }} warning(s)
        </Badge>
        <Badge
          v-else-if="editorContent"
          variant="success"
        >
          Valid
        </Badge>

        <!-- Unsaved indicator -->
        <Badge
          v-if="hasLocalChanges"
          variant="warning"
          dot
        >
          Unsaved
        </Badge>

        <!-- Undo/Redo -->
        <div class="flex items-center border-r border-border pr-2 mr-1">
          <Button
            variant="ghost"
            size="sm"
            :disabled="!canUndo"
            title="Undo (Ctrl+Z)"
            @click="handleUndo"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6" />
            </svg>
          </Button>
          <Button
            variant="ghost"
            size="sm"
            :disabled="!canRedo"
            title="Redo (Ctrl+Shift+Z)"
            @click="handleRedo"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 10h-10a8 8 0 00-8 8v2M21 10l-6 6m6-6l-6-6" />
            </svg>
          </Button>
        </div>

        <!-- Actions -->
        <Button
          variant="ghost"
          size="sm"
          :disabled="!hasLocalChanges"
          @click="handleDiscard"
        >
          Discard
        </Button>

        <Button
          variant="secondary"
          size="sm"
          @click="handleUpload"
          title="Upload config file"
        >
          Upload
        </Button>

        <Button
          variant="secondary"
          size="sm"
          @click="handleDownload"
          :disabled="!editorContent"
          title="Download config file"
        >
          Download
        </Button>

        <Button
          variant="secondary"
          size="sm"
          @click="showBackupsModal = true"
        >
          Backups
        </Button>

        <Button
          variant="secondary"
          size="sm"
          :loading="createBackupMutation.isPending.value"
          @click="handleBackup"
        >
          Create Backup
        </Button>

        <Button
          size="sm"
          :loading="saveConfigMutation.isPending.value"
          :disabled="!hasLocalChanges || !config.isValid"
          @click="handleSave"
        >
          Save
        </Button>
      </div>
    </div>

    <!-- Hidden file input for upload -->
    <input
      ref="fileInputRef"
      type="file"
      accept=".yml,.yaml"
      class="hidden"
      @change="handleFileChange"
    />

    <!-- Loading state -->
    <div
      v-if="isLoading"
      class="flex-1 flex items-center justify-center"
    >
      <Spinner size="lg" />
    </div>

    <!-- Error state -->
    <Card
      v-else-if="error"
      class="m-4"
    >
      <div class="text-center py-8">
        <div class="text-error mb-2">
          Failed to load configuration
        </div>
        <Button
          variant="secondary"
          size="sm"
          @click="refetch()"
        >
          Retry
        </Button>
      </div>
    </Card>

    <!-- Validation Panel (collapsible) -->
    <div
      v-if="!isLoading && !error && (config.hasErrors || config.hasWarnings)"
      class="border-b border-border"
    >
      <button
        class="w-full flex items-center justify-between p-3 hover:bg-surface-hover transition-colors"
        @click="showValidation = !showValidation"
      >
        <div class="flex items-center gap-2">
          <svg
            class="w-4 h-4 transition-transform"
            :class="{ 'rotate-90': showValidation }"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
          </svg>
          <span class="font-medium text-sm">Validation Issues</span>
          <Badge v-if="config.hasErrors" variant="error" size="sm">
            {{ config.validation.errors.length }}
          </Badge>
          <Badge v-if="config.hasWarnings" variant="warning" size="sm">
            {{ config.validation.warnings.length }}
          </Badge>
        </div>
        <span class="text-xs text-content-muted">
          {{ showValidation ? 'Click to hide' : 'Click to show details' }}
        </span>
      </button>
      <div
        v-if="showValidation"
        class="p-4 bg-surface-secondary max-h-64 overflow-auto"
      >
        <ValidationPanel />
      </div>
    </div>

    <!-- Config Editor with GUI/YAML split view -->
    <ConfigEditor
      v-else-if="!isLoading && !error"
      v-model="editorContent"
      class="flex-1 min-h-0"
      @test-connection="handleTestConnection"
    />

    <!-- Config Editor (when validation panel is visible) -->
    <ConfigEditor
      v-if="!isLoading && !error && (config.hasErrors || config.hasWarnings)"
      v-model="editorContent"
      class="flex-1 min-h-0"
      @test-connection="handleTestConnection"
    />

    <!-- Backups Modal -->
    <Modal
      v-model:open="showBackupsModal"
      title="Configuration Backups"
      size="md"
    >
      <div
        v-if="backups && backups.length > 0"
        class="space-y-2"
      >
        <div
          v-for="backup in backups"
          :key="backup.filename"
          class="flex items-center justify-between p-3 rounded-lg bg-surface-tertiary"
        >
          <div>
            <div class="font-medium text-sm">
              {{ backup.filename }}
            </div>
            <div class="text-xs text-content-muted">
              {{ formatDate(backup.created) }} - {{ formatSize(backup.size) }}
            </div>
          </div>
          <Button
            variant="secondary"
            size="sm"
            :loading="restoreBackupMutation.isPending.value"
            @click="handleRestore(backup.filename)"
          >
            Restore
          </Button>
        </div>
      </div>
      <div
        v-else
        class="text-center py-8 text-content-muted"
      >
        No backups available
      </div>
    </Modal>
  </div>
</template>
