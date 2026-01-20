<script setup lang="ts">
import { computed } from 'vue';
import type { ParityStatus } from '@/types';

interface Props {
  status: ParityStatus;
  showLabel?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  showLabel: true,
});

const statusConfig = computed(() => {
  switch (props.status) {
    case 'exact':
      return {
        label: 'Exact',
        description: 'Preview matches actual Kometa output',
        color: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
        icon: 'M5 13l4 4L19 7',
      };
    case 'exact_for_selected':
      return {
        label: 'Exact for Item',
        description: 'Accurate for this item, may differ for others',
        color: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
        icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z',
      };
    case 'risk':
      return {
        label: 'Approximate',
        description: 'Some values are samples or estimates',
        color: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
        icon: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z',
      };
    case 'not_supported':
      return {
        label: 'Not Supported',
        description: 'Cannot generate accurate preview',
        color: 'bg-red-500/20 text-red-400 border-red-500/30',
        icon: 'M6 18L18 6M6 6l12 12',
      };
    default:
      return {
        label: 'Unknown',
        description: 'Status unknown',
        color: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
        icon: 'M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
      };
  }
});
</script>

<template>
  <div
    :class="[
      'inline-flex items-center gap-1.5 px-2 py-1 rounded-md text-xs font-medium border',
      statusConfig.color
    ]"
    :title="statusConfig.description"
  >
    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="statusConfig.icon" />
    </svg>
    <span v-if="showLabel">{{ statusConfig.label }}</span>
  </div>
</template>
