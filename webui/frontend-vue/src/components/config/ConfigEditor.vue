<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { parse, stringify } from 'yaml';
import ConfigSectionNav, { type ConfigSection } from './ConfigSectionNav.vue';
import ViewModeToggle, { type ViewMode } from './ViewModeToggle.vue';
import {
  PlexSection,
  TMDbSection,
  LibrariesSection,
  SettingsSection,
  SchedulingSection,
  OperationsSection,
  RadarrSection,
  SonarrSection,
  TraktSection,
  TautulliSection,
  MALSection,
  NotifiarrSection,
  WebhooksSection,
  OMDbSection,
  MDBListSection,
  GitHubSection,
  AniDBSection,
  GotifySection,
  NtfySection,
} from './sections';
import { Card, YamlHighlight } from '@/components/common';

interface Props {
  modelValue: string; // YAML content
}

const props = defineProps<Props>();
const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void;
  (e: 'test-connection', service: string, config: Record<string, unknown>): void;
}>();

// View state
const viewMode = ref<ViewMode>('split');
const activeSection = ref('plex');
const showSectionOnly = ref(true); // In YAML mode, show section only by default
const isEditing = ref(false); // Toggle between view and edit mode in YAML panel

// Parse YAML to object for GUI editing
const parsedConfig = ref<Record<string, unknown>>({});
const parseError = ref<string | null>(null);

// Watch for external YAML changes
watch(
  () => props.modelValue,
  (yaml) => {
    try {
      parsedConfig.value = yaml ? parse(yaml) || {} : {};
      parseError.value = null;
    } catch (err) {
      parseError.value = err instanceof Error ? err.message : 'Invalid YAML';
    }
  },
  { immediate: true }
);

// Convert parsed config back to YAML when GUI changes
function updateConfig(section: string, value: unknown) {
  parsedConfig.value = {
    ...parsedConfig.value,
    [section]: value,
  };
  try {
    const yaml = stringify(parsedConfig.value, { lineWidth: 0 });
    emit('update:modelValue', yaml);
    parseError.value = null;
  } catch (err) {
    parseError.value = err instanceof Error ? err.message : 'Failed to generate YAML';
  }
}

// Section definitions
const sections: ConfigSection[] = [
  { id: 'plex', label: 'Plex', icon: '📺', group: 'Core', required: true },
  { id: 'tmdb', label: 'TMDb', icon: '🎬', group: 'Core', required: true },
  { id: 'libraries', label: 'Libraries', icon: '📚', group: 'Core', required: true },
  { id: 'settings', label: 'Settings', icon: '⚙️', group: 'Settings' },
  { id: 'scheduling', label: 'Scheduling', icon: '🕐', group: 'Settings' },
  { id: 'operations', label: 'Operations', icon: '⚡', group: 'Settings' },
  { id: 'radarr', label: 'Radarr', icon: '🎥', group: 'Integrations' },
  { id: 'sonarr', label: 'Sonarr', icon: '📺', group: 'Integrations' },
  { id: 'tautulli', label: 'Tautulli', icon: '📊', group: 'Integrations' },
  { id: 'trakt', label: 'Trakt', icon: '📋', group: 'Integrations' },
  { id: 'mal', label: 'MyAnimeList', icon: '🎌', group: 'Integrations' },
  { id: 'anidb', label: 'AniDB', icon: '🎌', group: 'Integrations' },
  { id: 'omdb', label: 'OMDb', icon: '🎬', group: 'Metadata' },
  { id: 'mdblist', label: 'MDBList', icon: '📋', group: 'Metadata' },
  { id: 'github', label: 'GitHub', icon: '🐙', group: 'Metadata' },
  { id: 'notifiarr', label: 'Notifiarr', icon: '🔔', group: 'Notifications' },
  { id: 'gotify', label: 'Gotify', icon: '📨', group: 'Notifications' },
  { id: 'ntfy', label: 'ntfy', icon: '🔔', group: 'Notifications' },
  { id: 'webhooks', label: 'Webhooks', icon: '🔗', group: 'Notifications' },
];

// Get section-specific config
const plexConfig = computed(() => (parsedConfig.value.plex as Record<string, unknown>) || {});
const tmdbConfig = computed(() => (parsedConfig.value.tmdb as Record<string, unknown>) || {});
const librariesConfig = computed(() => (parsedConfig.value.libraries as Record<string, unknown>) || {});
const settingsConfig = computed(() => (parsedConfig.value.settings as Record<string, unknown>) || {});
const schedulingConfig = computed(() => (parsedConfig.value.scheduling as Record<string, unknown>) || {});
const operationsConfig = computed(() => (parsedConfig.value.operations as Record<string, unknown>) || {});
const radarrConfig = computed(() => (parsedConfig.value.radarr as Record<string, unknown>) || {});
const sonarrConfig = computed(() => (parsedConfig.value.sonarr as Record<string, unknown>) || {});
const traktConfig = computed(() => (parsedConfig.value.trakt as Record<string, unknown>) || {});
const tautulliConfig = computed(() => (parsedConfig.value.tautulli as Record<string, unknown>) || {});
const malConfig = computed(() => (parsedConfig.value.mal as Record<string, unknown>) || {});
const notifiarrConfig = computed(() => (parsedConfig.value.notifiarr as Record<string, unknown>) || {});
const webhooksConfig = computed(() => (parsedConfig.value.webhooks as Record<string, unknown>) || {});
const omdbConfig = computed(() => (parsedConfig.value.omdb as Record<string, unknown>) || {});
const mdblistConfig = computed(() => (parsedConfig.value.mdblist as Record<string, unknown>) || {});
const githubConfig = computed(() => (parsedConfig.value.github as Record<string, unknown>) || {});
const anidbConfig = computed(() => (parsedConfig.value.anidb as Record<string, unknown>) || {});
const gotifyConfig = computed(() => (parsedConfig.value.gotify as Record<string, unknown>) || {});
const ntfyConfig = computed(() => (parsedConfig.value.ntfy as Record<string, unknown>) || {});

// YAML editor content (for direct editing)
const yamlContent = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
});

// Section-filtered YAML content (shows only the active section)
const sectionYamlContent = computed(() => {
  const sectionData = parsedConfig.value[activeSection.value];
  if (!sectionData) {
    return `# No ${activeSection.value} configuration yet\n# Add settings using the form on the left`;
  }
  try {
    return stringify({ [activeSection.value]: sectionData }, { lineWidth: 0 });
  } catch {
    return `# Error generating YAML for ${activeSection.value}`;
  }
});

// Content to display in YAML panel (respects showSectionOnly toggle)
const displayYamlContent = computed(() => {
  if (showSectionOnly.value) {
    return sectionYamlContent.value;
  }
  return props.modelValue || '# Empty configuration';
});
</script>

<template>
  <div class="h-full flex flex-col">
    <!-- Controls Bar -->
    <div class="flex items-center justify-between px-4 py-2 border-b border-border bg-surface-secondary">
      <ConfigSectionNav
        :sections="sections"
        :active-section="activeSection"
        @select="activeSection = $event"
      />
      <ViewModeToggle v-model="viewMode" />
    </div>

    <!-- Parse Error -->
    <div
      v-if="parseError && viewMode !== 'yaml'"
      class="px-4 py-2 bg-error/10 border-b border-error/20 text-error text-sm"
    >
      <strong>YAML Error:</strong> {{ parseError }}
    </div>

    <!-- Content Area -->
    <div
      class="flex-1 min-h-0 flex"
      :class="{
        'overflow-hidden': viewMode === 'split',
      }"
    >
      <!-- GUI Panel -->
      <div
        v-if="viewMode !== 'yaml'"
        class="flex-1 overflow-auto p-4"
        :class="{ 'border-r border-border': viewMode === 'split' }"
      >
        <!-- Plex Section -->
        <PlexSection
          v-if="activeSection === 'plex'"
          :model-value="plexConfig"
          @update:model-value="updateConfig('plex', $event)"
          @test-connection="emit('test-connection', 'plex', plexConfig)"
        />

        <!-- TMDb Section -->
        <TMDbSection
          v-else-if="activeSection === 'tmdb'"
          :model-value="tmdbConfig"
          @update:model-value="updateConfig('tmdb', $event)"
          @test-connection="emit('test-connection', 'tmdb', tmdbConfig)"
        />

        <!-- Libraries Section -->
        <LibrariesSection
          v-else-if="activeSection === 'libraries'"
          :model-value="librariesConfig"
          @update:model-value="updateConfig('libraries', $event)"
        />

        <!-- Settings Section -->
        <SettingsSection
          v-else-if="activeSection === 'settings'"
          :model-value="settingsConfig"
          @update:model-value="updateConfig('settings', $event)"
        />

        <!-- Scheduling Section -->
        <SchedulingSection
          v-else-if="activeSection === 'scheduling'"
          :model-value="schedulingConfig"
          @update:model-value="updateConfig('scheduling', $event)"
        />

        <!-- Operations Section -->
        <OperationsSection
          v-else-if="activeSection === 'operations'"
          :model-value="operationsConfig"
          @update:model-value="updateConfig('operations', $event)"
        />

        <!-- Radarr Section -->
        <RadarrSection
          v-else-if="activeSection === 'radarr'"
          :model-value="radarrConfig"
          @update:model-value="updateConfig('radarr', $event)"
          @test-connection="emit('test-connection', 'radarr', radarrConfig)"
        />

        <!-- Sonarr Section -->
        <SonarrSection
          v-else-if="activeSection === 'sonarr'"
          :model-value="sonarrConfig"
          @update:model-value="updateConfig('sonarr', $event)"
          @test-connection="emit('test-connection', 'sonarr', sonarrConfig)"
        />

        <!-- Trakt Section -->
        <TraktSection
          v-else-if="activeSection === 'trakt'"
          :model-value="traktConfig"
          @update:model-value="updateConfig('trakt', $event)"
        />

        <!-- Tautulli Section -->
        <TautulliSection
          v-else-if="activeSection === 'tautulli'"
          :model-value="tautulliConfig"
          @update:model-value="updateConfig('tautulli', $event)"
          @test-connection="emit('test-connection', 'tautulli', tautulliConfig)"
        />

        <!-- MAL Section -->
        <MALSection
          v-else-if="activeSection === 'mal'"
          :model-value="malConfig"
          @update:model-value="updateConfig('mal', $event)"
        />

        <!-- Notifiarr Section -->
        <NotifiarrSection
          v-else-if="activeSection === 'notifiarr'"
          :model-value="notifiarrConfig"
          @update:model-value="updateConfig('notifiarr', $event)"
          @test-connection="emit('test-connection', 'notifiarr', notifiarrConfig)"
        />

        <!-- Webhooks Section -->
        <WebhooksSection
          v-else-if="activeSection === 'webhooks'"
          :model-value="webhooksConfig"
          @update:model-value="updateConfig('webhooks', $event)"
        />

        <!-- OMDb Section -->
        <OMDbSection
          v-else-if="activeSection === 'omdb'"
          :model-value="omdbConfig"
          @update:model-value="updateConfig('omdb', $event)"
          @test-connection="emit('test-connection', 'omdb', omdbConfig)"
        />

        <!-- MDBList Section -->
        <MDBListSection
          v-else-if="activeSection === 'mdblist'"
          :model-value="mdblistConfig"
          @update:model-value="updateConfig('mdblist', $event)"
          @test-connection="emit('test-connection', 'mdblist', mdblistConfig)"
        />

        <!-- GitHub Section -->
        <GitHubSection
          v-else-if="activeSection === 'github'"
          :model-value="githubConfig"
          @update:model-value="updateConfig('github', $event)"
        />

        <!-- AniDB Section -->
        <AniDBSection
          v-else-if="activeSection === 'anidb'"
          :model-value="anidbConfig"
          @update:model-value="updateConfig('anidb', $event)"
          @test-connection="emit('test-connection', 'anidb', anidbConfig)"
        />

        <!-- Gotify Section -->
        <GotifySection
          v-else-if="activeSection === 'gotify'"
          :model-value="gotifyConfig"
          @update:model-value="updateConfig('gotify', $event)"
          @test-connection="emit('test-connection', 'gotify', gotifyConfig)"
        />

        <!-- ntfy Section -->
        <NtfySection
          v-else-if="activeSection === 'ntfy'"
          :model-value="ntfyConfig"
          @update:model-value="updateConfig('ntfy', $event)"
          @test-connection="emit('test-connection', 'ntfy', ntfyConfig)"
        />

        <!-- Placeholder for other sections -->
        <div
          v-else
          class="flex flex-col items-center justify-center h-full text-content-muted"
        >
          <span class="text-4xl mb-4">🚧</span>
          <p class="text-lg font-medium">{{ sections.find(s => s.id === activeSection)?.label }} Section</p>
          <p class="text-sm">This section is coming soon</p>
        </div>
      </div>

      <!-- YAML Panel -->
      <div
        v-if="viewMode !== 'gui'"
        class="flex-1 min-h-0 flex flex-col"
        :class="{ 'max-w-[50%]': viewMode === 'split' }"
      >
        <Card class="flex-1 flex flex-col min-h-0" padding="none">
          <template #header>
            <div class="flex items-center justify-between w-full">
              <div class="flex items-center gap-2">
                <span class="font-medium font-mono text-sm">
                  {{ showSectionOnly ? `${activeSection}:` : 'config.yml' }}
                </span>
                <span
                  v-if="showSectionOnly"
                  class="text-xs px-1.5 py-0.5 rounded bg-kometa-gold/20 text-kometa-gold"
                >
                  Section
                </span>
                <span
                  v-else
                  class="text-xs px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-400"
                >
                  Full Config
                </span>
              </div>
              <div class="flex items-center gap-2">
                <!-- Section/Full toggle -->
                <button
                  class="flex items-center gap-1 px-2 py-1 text-xs rounded transition-colors"
                  :class="showSectionOnly
                    ? 'bg-surface-tertiary text-content-secondary hover:text-content'
                    : 'bg-blue-500/20 text-blue-400'"
                  @click="showSectionOnly = !showSectionOnly"
                  :title="showSectionOnly ? 'Show full config' : 'Show section only'"
                >
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path v-if="showSectionOnly" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
                    <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 9V4.5M9 9H4.5M9 9L3.75 3.75M9 15v4.5M9 15H4.5M9 15l-5.25 5.25M15 9h4.5M15 9V4.5M15 9l5.25-5.25M15 15h4.5M15 15v4.5m0-4.5l5.25 5.25" />
                  </svg>
                  {{ showSectionOnly ? 'Full' : 'Section' }}
                </button>
                <!-- Edit toggle (only in YAML mode) -->
                <button
                  v-if="viewMode === 'yaml'"
                  class="flex items-center gap-1 px-2 py-1 text-xs rounded transition-colors"
                  :class="isEditing
                    ? 'bg-kometa-gold/20 text-kometa-gold'
                    : 'bg-surface-tertiary text-content-secondary hover:text-content'"
                  @click="isEditing = !isEditing"
                  :title="isEditing ? 'Switch to view mode' : 'Switch to edit mode'"
                >
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path v-if="isEditing" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path v-if="isEditing" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                  {{ isEditing ? 'View' : 'Edit' }}
                </button>
              </div>
            </div>
          </template>

          <div class="flex-1 min-h-0 relative">
            <!-- Edit mode: textarea -->
            <textarea
              v-if="viewMode === 'yaml' && isEditing"
              v-model="yamlContent"
              class="absolute inset-0 w-full h-full p-4 bg-surface-primary text-content font-mono text-sm
                     border-0 resize-none focus:ring-0 focus:outline-none overflow-auto"
              spellcheck="false"
              wrap="off"
              @keydown.tab.prevent="yamlContent += '  '"
            />
            <!-- View mode: syntax highlighted -->
            <div
              v-else
              class="absolute inset-0 w-full h-full p-4 bg-surface-primary overflow-auto"
            >
              <YamlHighlight :content="displayYamlContent" />
            </div>
          </div>
        </Card>
      </div>
    </div>
  </div>
</template>
