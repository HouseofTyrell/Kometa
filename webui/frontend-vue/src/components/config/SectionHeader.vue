<script setup lang="ts">
/**
 * Reusable section header for config sections.
 * Eliminates duplicate header layout across 20+ config sections.
 */
interface Props {
  /** Icon emoji for the section */
  icon: string;
  /** Section title */
  title: string;
  /** Section description */
  description: string;
  /** Documentation URL */
  docsUrl?: string;
  /** Whether the section is required */
  required?: boolean;
  /** Whether the section is optional (default) */
  optional?: boolean;
}

withDefaults(defineProps<Props>(), {
  docsUrl: undefined,
  required: false,
  optional: false,
});
</script>

<template>
  <div class="flex items-start justify-between">
    <div>
      <div class="flex items-center gap-2">
        <span class="text-2xl">{{ icon }}</span>
        <h3 class="text-lg font-semibold">{{ title }}</h3>
        <span
          v-if="required"
          class="text-xs px-2 py-0.5 rounded bg-error/20 text-error font-medium"
        >
          Required
        </span>
        <span
          v-else-if="optional"
          class="text-xs px-2 py-0.5 rounded bg-surface-tertiary text-content-muted font-medium"
        >
          Optional
        </span>
      </div>
      <p class="mt-1 text-sm text-content-secondary">
        {{ description }}
      </p>
    </div>
    <a
      v-if="docsUrl"
      :href="docsUrl"
      target="_blank"
      class="flex items-center gap-1 text-sm text-kometa-gold hover:underline flex-shrink-0"
    >
      <svg
        class="w-4 h-4"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
        />
      </svg>
      Documentation
    </a>
  </div>
</template>
