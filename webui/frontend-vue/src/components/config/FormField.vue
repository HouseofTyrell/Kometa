<script setup lang="ts">
interface Props {
  label: string;
  required?: boolean;
  tooltip?: string;
  help?: string;
  defaultValue?: string;
  error?: string;
}

defineProps<Props>();
</script>

<template>
  <div class="form-field">
    <label class="flex items-center gap-1.5 text-sm font-medium text-content mb-1.5">
      {{ label }}
      <span v-if="required" class="text-error">*</span>
      <span v-if="defaultValue" class="text-xs px-1.5 py-0.5 rounded bg-surface-tertiary text-content-muted">
        Default: {{ defaultValue }}
      </span>
      <span
        v-if="tooltip"
        class="relative group cursor-help"
      >
        <span class="inline-flex items-center justify-center w-4 h-4 rounded-full bg-surface-tertiary text-content-muted text-xs">
          ?
        </span>
        <span class="absolute left-1/2 -translate-x-1/2 bottom-full mb-2 px-3 py-2 text-sm bg-surface-primary
                     border border-border rounded-lg shadow-lg w-64 opacity-0 invisible
                     group-hover:opacity-100 group-hover:visible transition-all z-50 text-content-secondary font-normal">
          {{ tooltip }}
        </span>
      </span>
    </label>
    <slot />
    <p v-if="help" class="mt-1 text-xs text-content-muted">
      {{ help }}
    </p>
    <p v-if="error" class="mt-1 text-xs text-error">
      {{ error }}
    </p>
  </div>
</template>
