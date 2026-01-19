<script setup lang="ts">
import { computed } from 'vue';
import FormField from '../FormField.vue';
import { Input, Select } from '@/components/common';

interface TMDbConfig {
  apikey?: string;
  language?: string;
  region?: string;
  cache_expiration?: number;
}

interface Props {
  modelValue: TMDbConfig;
}

const props = defineProps<Props>();
const emit = defineEmits<{
  (e: 'update:modelValue', value: TMDbConfig): void;
  (e: 'test-connection'): void;
}>();

const config = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
});

function updateField<K extends keyof TMDbConfig>(field: K, value: TMDbConfig[K]) {
  emit('update:modelValue', { ...props.modelValue, [field]: value });
}

const languages = [
  { value: 'en', label: 'English' },
  { value: 'es', label: 'Spanish' },
  { value: 'fr', label: 'French' },
  { value: 'de', label: 'German' },
  { value: 'it', label: 'Italian' },
  { value: 'pt', label: 'Portuguese' },
  { value: 'ja', label: 'Japanese' },
  { value: 'ko', label: 'Korean' },
  { value: 'zh', label: 'Chinese' },
];

const regions = [
  { value: 'US', label: 'United States' },
  { value: 'GB', label: 'United Kingdom' },
  { value: 'CA', label: 'Canada' },
  { value: 'AU', label: 'Australia' },
  { value: 'DE', label: 'Germany' },
  { value: 'FR', label: 'France' },
  { value: 'ES', label: 'Spain' },
  { value: 'IT', label: 'Italy' },
  { value: 'JP', label: 'Japan' },
];
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-start justify-between">
      <div>
        <div class="flex items-center gap-2">
          <span class="text-2xl">🎬</span>
          <h3 class="text-lg font-semibold">TMDb Configuration</h3>
          <span class="text-xs px-2 py-0.5 rounded bg-error/20 text-error font-medium">Required</span>
        </div>
        <p class="mt-1 text-sm text-content-secondary">
          Configure The Movie Database (TMDb) API for metadata, images, and collection builders.
        </p>
      </div>
      <a
        href="https://kometa.wiki/en/latest/config/tmdb/"
        target="_blank"
        class="flex items-center gap-1 text-sm text-kometa-gold hover:underline"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
        </svg>
        Documentation
      </a>
    </div>

    <!-- API Key -->
    <FormField
      label="TMDb API Key"
      required
      tooltip="Your TMDb API key (v3 auth). Get one free at themoviedb.org."
    >
      <Input
        type="password"
        :model-value="config.apikey || ''"
        placeholder="Your TMDb API key"
        @update:model-value="updateField('apikey', $event)"
      />
      <template #help>
        <a
          href="https://www.themoviedb.org/settings/api"
          target="_blank"
          class="text-kometa-gold hover:underline"
        >
          Get your API key from TMDb ↗
        </a>
      </template>
    </FormField>

    <!-- Language & Region -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <FormField
        label="Language"
        default-value="en"
        tooltip="Primary language for TMDb metadata and titles"
        help="Language code for TMDb results"
      >
        <Select
          :model-value="config.language || 'en'"
          :options="languages"
          @update:model-value="updateField('language', $event)"
        />
      </FormField>

      <FormField
        label="Region"
        default-value="US"
        tooltip="Region for release dates and certifications"
        help="Country code for regional data"
      >
        <Select
          :model-value="config.region || 'US'"
          :options="regions"
          @update:model-value="updateField('region', $event)"
        />
      </FormField>
    </div>

    <!-- Cache -->
    <FormField
      label="Cache Expiration"
      default-value="60"
      tooltip="How long to cache TMDb data before refreshing (in days)"
      help="Days to cache TMDb data"
    >
      <Input
        type="number"
        :model-value="String(config.cache_expiration || 60)"
        @update:model-value="updateField('cache_expiration', Number($event))"
        min="1"
        max="365"
      />
    </FormField>

    <!-- Test Connection -->
    <div class="flex items-center gap-4 p-4 rounded-lg bg-surface-tertiary">
      <button
        class="px-4 py-2 rounded-lg bg-kometa-gold text-black font-medium hover:bg-kometa-gold/90 transition-colors"
        @click="emit('test-connection')"
      >
        Test Connection
      </button>
      <span class="text-sm text-content-secondary">
        Verify your TMDb API key is valid
      </span>
    </div>
  </div>
</template>
