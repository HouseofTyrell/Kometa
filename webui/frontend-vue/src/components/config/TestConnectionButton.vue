<script setup lang="ts">
/**
 * Reusable test connection button for config sections.
 * Eliminates duplicate button styling across 12+ config sections.
 */
interface Props {
  /** Loading state */
  loading?: boolean;
  /** Custom label text */
  label?: string;
  /** Description text next to button */
  description?: string;
}

withDefaults(defineProps<Props>(), {
  loading: false,
  label: 'Test Connection',
  description: undefined,
});

const emit = defineEmits<{
  (e: 'test'): void;
}>();
</script>

<template>
  <div class="flex items-center gap-4 p-4 rounded-lg bg-surface-tertiary">
    <button
      class="px-4 py-2 rounded-lg bg-kometa-gold text-black font-medium hover:bg-kometa-gold/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
      :disabled="loading"
      @click="emit('test')"
    >
      <svg
        v-if="loading"
        class="w-4 h-4 animate-spin"
        fill="none"
        viewBox="0 0 24 24"
      >
        <circle
          class="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          stroke-width="4"
        />
        <path
          class="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        />
      </svg>
      {{ label }}
    </button>
    <span
      v-if="description"
      class="text-sm text-content-secondary"
    >
      {{ description }}
    </span>
    <slot />
  </div>
</template>
