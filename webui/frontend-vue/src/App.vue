<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useUIStore, useRunStore, useConfigStore } from '@/stores';
import { useRunStatus, useConfig } from '@/api';
import TheHeader from '@/components/layout/TheHeader.vue';
import TheSidebar from '@/components/layout/TheSidebar.vue';
import MainContent from '@/components/layout/MainContent.vue';
import SetupWizard from '@/components/SetupWizard.vue';
import { ToastContainer, ConfirmDialog } from '@/components/common';

const ui = useUIStore();
const run = useRunStore();
const configStore = useConfigStore();

// Fetch run status on mount and poll while running
const { data: runStatus } = useRunStatus();

// Fetch config on mount
const { data: configData, isLoading: configLoading } = useConfig();

// Update config store when data loads
watch(configData, (data) => {
  if (data) {
    configStore.setRawConfig(data.content, false);
    if (data.parsed) {
      configStore.setParsedConfig(data.parsed);
    }
  }
});

// Update run store when status changes
const isRunning = computed(() => runStatus.value?.is_running ?? false);

// Setup wizard state
const showSetupWizard = ref(false);
const setupSkipped = ref(false);

// Check if setup is needed (no plex or tmdb configured)
const needsSetup = computed(() => {
  if (configLoading.value || setupSkipped.value) return false;

  const parsed = configStore.parsedConfig;
  if (!parsed) return true;

  // Check for required config sections
  const hasPlex = parsed.plex?.url && parsed.plex?.token;
  const hasTmdb = parsed.tmdb?.apikey;

  return !hasPlex || !hasTmdb;
});

// Show wizard when setup is needed
watch(needsSetup, (needs) => {
  if (needs && !setupSkipped.value) {
    showSetupWizard.value = true;
  }
}, { immediate: true });

function handleSetupComplete() {
  showSetupWizard.value = false;
}

function handleSetupSkip() {
  setupSkipped.value = true;
  showSetupWizard.value = false;
}
</script>

<template>
  <div class="min-h-screen bg-surface-base flex flex-col">
    <!-- Safety Banner -->
    <div
      :class="[
        'px-5 py-2 text-center font-semibold text-sm sticky top-0 z-50',
        run.applyEnabled
          ? 'bg-error text-white'
          : 'bg-success text-white',
      ]"
    >
      <template v-if="run.applyEnabled">
        APPLY MODE ENABLED - Changes will be applied to your Plex library
      </template>
      <template v-else>
        SAFE MODE - Dry run only, no changes will be made
      </template>
    </div>

    <!-- Main Layout -->
    <div class="flex flex-1 overflow-hidden">
      <!-- Sidebar -->
      <TheSidebar />

      <!-- Main Content Area -->
      <div class="flex-1 flex flex-col overflow-hidden">
        <!-- Header -->
        <TheHeader :is-running="isRunning" />

        <!-- Content -->
        <main class="flex-1 overflow-auto p-4">
          <MainContent />
        </main>
      </div>
    </div>

    <!-- Toast Notifications -->
    <ToastContainer />

    <!-- Confirm Dialog -->
    <ConfirmDialog />

    <!-- Setup Wizard -->
    <SetupWizard
      v-if="showSetupWizard"
      @complete="handleSetupComplete"
      @skip="handleSetupSkip"
    />
  </div>
</template>
