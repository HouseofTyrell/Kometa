<script setup lang="ts">
import { ref, onErrorCaptured } from 'vue';
import Button from './Button.vue';

interface Props {
  fallbackMessage?: string;
}

const props = withDefaults(defineProps<Props>(), {
  fallbackMessage: 'Something went wrong. Please try again.',
});

const emit = defineEmits<{
  (e: 'error', error: Error): void;
}>();

const error = ref<Error | null>(null);
const errorInfo = ref<string>('');

const reset = () => {
  error.value = null;
  errorInfo.value = '';
};

onErrorCaptured((err: Error, instance, info) => {
  error.value = err;
  errorInfo.value = info;
  emit('error', err);

  // Log the error for debugging
  console.error('Error caught by ErrorBoundary:', err);
  console.error('Component:', instance);
  console.error('Info:', info);

  // Return false to prevent error from propagating
  return false;
});
</script>

<template>
  <div v-if="error" class="error-boundary p-6 bg-error-bg border border-error rounded-lg">
    <div class="flex items-start gap-4">
      <div class="flex-shrink-0">
        <svg
          class="w-8 h-8 text-error"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
          />
        </svg>
      </div>
      <div class="flex-1">
        <h3 class="text-lg font-semibold text-error">
          An error occurred
        </h3>
        <p class="mt-1 text-content-secondary">
          {{ fallbackMessage }}
        </p>
        <details
          v-if="error.message"
          class="mt-3"
        >
          <summary class="cursor-pointer text-sm text-content-secondary hover:text-content">
            Show error details
          </summary>
          <div class="mt-2 p-3 bg-surface-tertiary rounded text-sm font-mono overflow-auto">
            <p class="text-error">{{ error.name }}: {{ error.message }}</p>
            <p v-if="errorInfo" class="mt-1 text-content-muted">
              Component lifecycle: {{ errorInfo }}
            </p>
            <pre
              v-if="error.stack"
              class="mt-2 text-xs text-content-muted whitespace-pre-wrap"
            >{{ error.stack }}</pre>
          </div>
        </details>
        <div class="mt-4">
          <Button
            variant="secondary"
            size="sm"
            @click="reset"
          >
            Try again
          </Button>
        </div>
      </div>
    </div>
  </div>
  <slot v-else />
</template>
