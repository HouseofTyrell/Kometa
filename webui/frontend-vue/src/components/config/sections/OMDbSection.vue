<script setup lang="ts">
import { computed } from 'vue';
import FormField from '../FormField.vue';
import SectionHeader from '../SectionHeader.vue';
import TestConnectionButton from '../TestConnectionButton.vue';
import { Input } from '@/components/common';
import { useConfigSection } from '@/composables';

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

const { updateField } = useConfigSection<OMDbConfig>(props, emit);

const hasApiKey = computed(() => !!props.modelValue.apikey);
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <SectionHeader
      icon="🎬"
      title="OMDb Configuration"
      description="Connect to the Open Movie Database (OMDb) for additional movie metadata and ratings."
      docs-url="https://kometa.wiki/en/latest/config/omdb/"
      optional
    />

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
    <TestConnectionButton
      v-if="hasApiKey"
      description="Verify your OMDb API key is working"
      @test="emit('test-connection')"
    />

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
