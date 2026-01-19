<script setup lang="ts">
import { computed } from 'vue';
import { useConfigStore } from '@/stores';
import { Card, Badge } from '@/components/common';

const config = useConfigStore();

interface ValidationItem {
  field?: string;
  message: string;
  suggestion?: string;
  line?: number;
  column?: number;
}

// Normalize errors/warnings to ValidationItem format (handle both old string[] and new object[] formats)
const normalizedErrors = computed((): ValidationItem[] => {
  return config.validation.errors.map((e) =>
    typeof e === 'string' ? { message: e } : e
  );
});

const normalizedWarnings = computed((): ValidationItem[] => {
  return config.validation.warnings.map((w) =>
    typeof w === 'string' ? { message: w } : w
  );
});

const hasIssues = computed(() =>
  normalizedErrors.value.length > 0 || normalizedWarnings.value.length > 0
);
</script>

<template>
  <div
    v-if="hasIssues"
    class="space-y-3"
  >
    <!-- Errors -->
    <div
      v-if="normalizedErrors.length > 0"
      class="space-y-2"
    >
      <div class="flex items-center gap-2">
        <Badge variant="error">
          {{ normalizedErrors.length }} Error{{ normalizedErrors.length === 1 ? '' : 's' }}
        </Badge>
        <span class="text-sm text-content-secondary">Must fix before saving</span>
      </div>

      <div
        v-for="(error, idx) in normalizedErrors"
        :key="`error-${idx}`"
        class="p-3 rounded-lg bg-error/10 border border-error/20"
      >
        <div class="flex items-start gap-2">
          <svg
            class="w-5 h-5 text-error flex-shrink-0 mt-0.5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 flex-wrap">
              <span
                v-if="error.field"
                class="text-xs font-mono px-1.5 py-0.5 rounded bg-error/20 text-error"
              >
                {{ error.field }}
              </span>
              <span
                v-if="error.line"
                class="text-xs text-error/80"
              >
                Line {{ error.line }}{{ error.column ? `:${error.column}` : '' }}
              </span>
            </div>
            <p class="text-sm text-error font-medium mt-1">
              {{ error.message }}
            </p>
            <p
              v-if="error.suggestion"
              class="text-xs text-content-secondary mt-1.5 whitespace-pre-wrap"
            >
              <strong>Fix:</strong> {{ error.suggestion }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Warnings -->
    <div
      v-if="normalizedWarnings.length > 0"
      class="space-y-2"
    >
      <div class="flex items-center gap-2">
        <Badge variant="warning">
          {{ normalizedWarnings.length }} Warning{{ normalizedWarnings.length === 1 ? '' : 's' }}
        </Badge>
        <span class="text-sm text-content-secondary">Recommended to review</span>
      </div>

      <div
        v-for="(warning, idx) in normalizedWarnings"
        :key="`warning-${idx}`"
        class="p-3 rounded-lg bg-warning/10 border border-warning/20"
      >
        <div class="flex items-start gap-2">
          <svg
            class="w-5 h-5 text-warning flex-shrink-0 mt-0.5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
            />
          </svg>
          <div class="flex-1 min-w-0">
            <span
              v-if="warning.field"
              class="text-xs font-mono px-1.5 py-0.5 rounded bg-warning/20 text-warning"
            >
              {{ warning.field }}
            </span>
            <p class="text-sm text-warning font-medium mt-1">
              {{ warning.message }}
            </p>
            <p
              v-if="warning.suggestion"
              class="text-xs text-content-secondary mt-1.5"
            >
              <strong>Suggestion:</strong> {{ warning.suggestion }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- All good state -->
  <div
    v-else-if="config.rawConfig"
    class="p-3 rounded-lg bg-success/10 border border-success/20"
  >
    <div class="flex items-center gap-2">
      <svg
        class="w-5 h-5 text-success"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
      <span class="text-sm text-success font-medium">Configuration is valid</span>
    </div>
  </div>
</template>
