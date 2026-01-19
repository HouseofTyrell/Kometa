<script setup lang="ts">
export type ViewMode = 'gui' | 'split' | 'yaml';

interface Props {
  modelValue: ViewMode;
}

defineProps<Props>();
const emit = defineEmits<{
  (e: 'update:modelValue', value: ViewMode): void;
}>();

const modes: { id: ViewMode; label: string; icon: string }[] = [
  { id: 'gui', label: 'GUI', icon: 'form' },
  { id: 'split', label: 'Split', icon: 'split' },
  { id: 'yaml', label: 'YAML', icon: 'code' },
];
</script>

<template>
  <div class="flex items-center gap-2">
    <span class="text-sm text-content-muted">View:</span>
    <div class="flex rounded-lg bg-surface-tertiary p-0.5">
      <button
        v-for="mode in modes"
        :key="mode.id"
        class="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm transition-colors"
        :class="modelValue === mode.id
          ? 'bg-surface-primary text-content shadow-sm'
          : 'text-content-secondary hover:text-content'"
        @click="emit('update:modelValue', mode.id)"
      >
        <!-- Form icon -->
        <svg v-if="mode.icon === 'form'" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <rect x="3" y="3" width="18" height="18" rx="2" stroke-width="2" />
          <line x1="9" y1="9" x2="15" y2="9" stroke-width="2" />
          <line x1="9" y1="13" x2="15" y2="13" stroke-width="2" />
          <line x1="9" y1="17" x2="12" y2="17" stroke-width="2" />
        </svg>
        <!-- Split icon -->
        <svg v-else-if="mode.icon === 'split'" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <rect x="3" y="3" width="18" height="18" rx="2" stroke-width="2" />
          <line x1="12" y1="3" x2="12" y2="21" stroke-width="2" />
        </svg>
        <!-- Code icon -->
        <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <rect x="3" y="3" width="18" height="18" rx="2" stroke-width="2" />
          <polyline points="8,8 6,10 8,12" stroke-width="2" />
          <polyline points="16,8 18,10 16,12" stroke-width="2" />
          <line x1="10" y1="16" x2="14" y2="16" stroke-width="2" />
        </svg>
        <span>{{ mode.label }}</span>
      </button>
    </div>
  </div>
</template>
