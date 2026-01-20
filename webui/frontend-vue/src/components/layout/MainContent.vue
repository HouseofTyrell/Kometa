<script setup lang="ts">
import { useUIStore } from '@/stores';

// Tab content components
import DashboardTab from '@/components/tabs/DashboardTab.vue';
import ConfigTab from '@/components/tabs/ConfigTab.vue';
import CollectionsTab from '@/components/tabs/CollectionsTab.vue';
import PlaylistsTab from '@/components/tabs/PlaylistsTab.vue';
import RunTab from '@/components/tabs/RunTab.vue';
import LogsTab from '@/components/tabs/LogsTab.vue';
import HistoryTab from '@/components/tabs/HistoryTab.vue';
import MediaTab from '@/components/tabs/MediaTab.vue';
import MetadataTab from '@/components/tabs/MetadataTab.vue';
import OverlaysTab from '@/components/tabs/OverlaysTab.vue';
import SettingsTab from '@/components/tabs/SettingsTab.vue';

const ui = useUIStore();

const tabs = {
  dashboard: DashboardTab,
  config: ConfigTab,
  collections: CollectionsTab,
  playlists: PlaylistsTab,
  run: RunTab,
  logs: LogsTab,
  history: HistoryTab,
  media: MediaTab,
  metadata: MetadataTab,
  overlays: OverlaysTab,
  settings: SettingsTab,
};
</script>

<template>
  <div class="h-full">
    <Transition
      name="fade"
      mode="out-in"
    >
      <component
        :is="tabs[ui.activeTab]"
        :key="ui.activeTab"
      />
    </Transition>
  </div>
</template>
