<script setup lang="ts">
import { computed } from 'vue';
import FormField from '../FormField.vue';
import { Input } from '@/components/common';

interface OMDbConfig {
  apikey?: string;
  cache_expiration?: number;
}

interface Props {
  modelValue: OMDbConfig;
}

const props = defineProps<Props>();
const emit = defineEmits<{
  (e: 'update:modelValue', value: OMDbConfig): void;
  (e: 'test-connection'): void;
}>();

function updateField<K extends keyof OMDbConfig>(field: K, value: OMDbConfig[K]) {
  emit('update:modelValue', { ...props.modelValue, [field]: value });
}

const hasApiKey = computed(() => !!props.modelValue.apikey);
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-start justify-between">
      <div>
        <div class="flex items-center gap-2">
          <span class="text-2xl">🎬</span>
          <h3 class="text-lg font-semibold">OMDb Configuration</h3>
          <span class="text-xs px-2 py-0.5 rounded bg-surface-tertiary text-content-muted font-medium">Optional</span>
        </div>
        <p class="mt-1 text-sm text-content-secondary">
          Connect to the Open Movie Database (OMDb) for additional movie metadata and ratings.
        </p>
      </div>
      <a
        href="https://kometa.wiki/en/latest/config/omdb/"
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

    <!-- Connection Status -->
    <div
      class="p-4 rounded-lg"
      :class="hasApiKey ? 'bg-success/10 border border-success/20' : 'bg-surface-tertiary'"
    >
      <div class="flex items-center gap-3">
        <span :class="hasApiKey ? 'text-success' : 'text-content-muted'" class="text-xl">
          {{ hasApiKey ? '✓' : '🎬' }}
        </span>
        <div class="flex-1">
          <p class="font-medium" :class="hasApiKey ? 'text-success' : 'text-content'">
            {{ hasApiKey ? 'OMDb Connected' : 'Connect OMDb' }}
          </p>
          <p class="text-sm text-content-secondary">
            {{ hasApiKey
              ? 'Your OMDb API key is configured.'
              : 'Enter your OMDb API key to access additional movie data.' }}
          </p>
        </div>
      </div>
    </div>

    <!-- API Key -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <FormField
        label="API Key"
        required
        tooltip="Your OMDb API key from omdbapi.com"
        help="Get a free API key at omdbapi.com/apikey.aspx"
      >
        <Input
          type="password"
          :model-value="props.modelValue.apikey || ''"
          placeholder="Your OMDb API key"
          @update:model-value="updateField('apikey', $event)"
        />
      </FormField>

      <FormField
        label="Cache Expiration"
        tooltip="Number of days to cache OMDb data"
        help="Default: 60 days"
      >
        <Input
          type="number"
          :model-value="String(props.modelValue.cache_expiration || '')"
          placeholder="60"
          min="1"
          @update:model-value="updateField('cache_expiration', $event ? Number($event) : undefined)"
        />
      </FormField>
    </div>

    <!-- Test Connection -->
    <div v-if="hasApiKey" class="flex items-center gap-4 p-4 rounded-lg bg-surface-tertiary">
      <button
        class="px-4 py-2 rounded-lg bg-kometa-gold text-black font-medium hover:bg-kometa-gold/90 transition-colors"
        @click="emit('test-connection')"
      >
        Test Connection
      </button>
      <span class="text-sm text-content-secondary">
        Verify your OMDb API key is working
      </span>
    </div>

    <!-- Usage Examples -->
    <div class="border-t border-border pt-6">
      <h4 class="font-medium mb-4 flex items-center gap-2">
        <span>📚</span> OMDb Data Sources
      </h4>
      <p class="text-sm text-content-secondary mb-4">
        Once connected, you can use OMDb as a source for mass updates:
      </p>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
        <div class="p-3 rounded bg-surface-tertiary">
          <code class="text-kometa-gold">mass_audience_rating_update: omdb</code>
          <p class="text-content-secondary mt-1">IMDb ratings from OMDb</p>
        </div>
        <div class="p-3 rounded bg-surface-tertiary">
          <code class="text-kometa-gold">mass_genre_update: omdb</code>
          <p class="text-content-secondary mt-1">Genre data from OMDb</p>
        </div>
      </div>
    </div>

    <!-- How It Works -->
    <div class="border-t border-border pt-6">
      <h4 class="font-medium mb-4 flex items-center gap-2">
        <span>💡</span> About OMDb
      </h4>
      <div class="p-4 rounded-lg bg-surface-tertiary text-sm">
        <p class="text-content-secondary mb-3">
          OMDb (Open Movie Database) provides movie and TV show information:
        </p>
        <ul class="list-disc list-inside space-y-1 text-content-secondary">
          <li>IMDb ratings and vote counts</li>
          <li>Rotten Tomatoes scores</li>
          <li>Metacritic ratings</li>
          <li>Genre, director, writer, and actor information</li>
          <li>Box office data</li>
        </ul>
        <p class="mt-3">
          <a
            href="https://www.omdbapi.com/apikey.aspx"
            target="_blank"
            class="text-kometa-gold hover:underline"
          >
            Get a free API key at omdbapi.com →
          </a>
        </p>
      </div>
    </div>
  </div>
</template>
