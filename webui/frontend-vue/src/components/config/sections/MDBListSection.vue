<script setup lang="ts">
import { computed } from 'vue';
import FormField from '../FormField.vue';
import { Input } from '@/components/common';

interface MDBListConfig {
  apikey?: string;
  cache_expiration?: number;
}

interface Props {
  modelValue: MDBListConfig;
}

const props = defineProps<Props>();
const emit = defineEmits<{
  (e: 'update:modelValue', value: MDBListConfig): void;
  (e: 'test-connection'): void;
}>();

function updateField<K extends keyof MDBListConfig>(field: K, value: MDBListConfig[K]) {
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
          <span class="text-2xl">📋</span>
          <h3 class="text-lg font-semibold">MDBList Configuration</h3>
          <span class="text-xs px-2 py-0.5 rounded bg-surface-tertiary text-content-muted font-medium">Optional</span>
        </div>
        <p class="mt-1 text-sm text-content-secondary">
          Connect MDBList to access curated lists, ratings from multiple sources, and advanced filtering.
        </p>
      </div>
      <a
        href="https://kometa.wiki/en/latest/config/mdblist/"
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
          {{ hasApiKey ? '✓' : '📋' }}
        </span>
        <div class="flex-1">
          <p class="font-medium" :class="hasApiKey ? 'text-success' : 'text-content'">
            {{ hasApiKey ? 'MDBList Connected' : 'Connect MDBList' }}
          </p>
          <p class="text-sm text-content-secondary">
            {{ hasApiKey
              ? 'Your MDBList API key is configured.'
              : 'Enter your MDBList API key to access curated lists and ratings.' }}
          </p>
        </div>
      </div>
    </div>

    <!-- API Key -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <FormField
        label="API Key"
        required
        tooltip="Your MDBList API key"
        help="Get your API key at mdblist.com"
      >
        <Input
          type="password"
          :model-value="props.modelValue.apikey || ''"
          placeholder="Your MDBList API key"
          @update:model-value="updateField('apikey', $event)"
        />
      </FormField>

      <FormField
        label="Cache Expiration"
        tooltip="Number of days to cache MDBList data"
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
        Verify your MDBList API key is working
      </span>
    </div>

    <!-- Usage Examples -->
    <div class="border-t border-border pt-6">
      <h4 class="font-medium mb-4 flex items-center gap-2">
        <span>📚</span> MDBList Builders
      </h4>
      <p class="text-sm text-content-secondary mb-4">
        Once connected, you can use MDBList builders in your collection files:
      </p>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
        <div class="p-3 rounded bg-surface-tertiary">
          <code class="text-kometa-gold">mdblist_list</code>
          <p class="text-content-secondary mt-1">Build collections from MDBList lists</p>
        </div>
        <div class="p-3 rounded bg-surface-tertiary">
          <code class="text-kometa-gold">mdb_average / mdb</code>
          <p class="text-content-secondary mt-1">Use MDBList ratings for mass updates</p>
        </div>
      </div>
    </div>

    <!-- Rating Sources -->
    <div class="border-t border-border pt-6">
      <h4 class="font-medium mb-4 flex items-center gap-2">
        <span>⭐</span> Available Rating Sources
      </h4>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm">
        <div class="p-2 rounded bg-surface-tertiary text-center">IMDb</div>
        <div class="p-2 rounded bg-surface-tertiary text-center">TMDb</div>
        <div class="p-2 rounded bg-surface-tertiary text-center">Trakt</div>
        <div class="p-2 rounded bg-surface-tertiary text-center">Letterboxd</div>
        <div class="p-2 rounded bg-surface-tertiary text-center">Rotten Tomatoes</div>
        <div class="p-2 rounded bg-surface-tertiary text-center">Metacritic</div>
        <div class="p-2 rounded bg-surface-tertiary text-center">MyAnimeList</div>
        <div class="p-2 rounded bg-surface-tertiary text-center">AniList</div>
      </div>
    </div>

    <!-- How It Works -->
    <div class="border-t border-border pt-6">
      <h4 class="font-medium mb-4 flex items-center gap-2">
        <span>💡</span> About MDBList
      </h4>
      <div class="p-4 rounded-lg bg-surface-tertiary text-sm">
        <p class="text-content-secondary mb-3">
          MDBList aggregates ratings and lists from multiple sources:
        </p>
        <ul class="list-disc list-inside space-y-1 text-content-secondary">
          <li>Create and share custom lists</li>
          <li>Filter by ratings across multiple platforms</li>
          <li>Get averaged scores from all rating sources</li>
          <li>Access community-curated lists</li>
          <li>Track streaming availability</li>
        </ul>
        <p class="mt-3">
          <a
            href="https://mdblist.com"
            target="_blank"
            class="text-kometa-gold hover:underline"
          >
            Create a free account at mdblist.com →
          </a>
        </p>
      </div>
    </div>
  </div>
</template>
