<script setup lang="ts">
import { computed } from 'vue';
import FormField from '../FormField.vue';
import { Input, Select } from '@/components/common';

interface AniDBConfig {
  username?: string;
  password?: string;
  client?: string;
  version?: number;
  cache_expiration?: number;
  language?: string;
}

interface Props {
  modelValue: AniDBConfig;
}

const props = defineProps<Props>();
const emit = defineEmits<{
  (e: 'update:modelValue', value: AniDBConfig): void;
  (e: 'test-connection'): void;
}>();

function updateField<K extends keyof AniDBConfig>(field: K, value: AniDBConfig[K]) {
  emit('update:modelValue', { ...props.modelValue, [field]: value });
}

const isConfigured = computed(() =>
  !!props.modelValue.username &&
  !!props.modelValue.password &&
  !!props.modelValue.client
);

const languageOptions = [
  { value: '', label: 'Default (English)' },
  { value: 'en', label: 'English' },
  { value: 'ja', label: 'Japanese' },
  { value: 'x-jat', label: 'Romaji' },
  { value: 'de', label: 'German' },
  { value: 'fr', label: 'French' },
  { value: 'ko', label: 'Korean' },
  { value: 'zh-Hans', label: 'Chinese (Simplified)' },
  { value: 'zh-Hant', label: 'Chinese (Traditional)' },
];
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-start justify-between">
      <div>
        <div class="flex items-center gap-2">
          <span class="text-2xl">🎌</span>
          <h3 class="text-lg font-semibold">AniDB Configuration</h3>
          <span class="text-xs px-2 py-0.5 rounded bg-surface-tertiary text-content-muted font-medium">Optional</span>
        </div>
        <p class="mt-1 text-sm text-content-secondary">
          Connect AniDB for anime metadata, relations, and additional information.
        </p>
      </div>
      <a
        href="https://kometa.wiki/en/latest/config/anidb/"
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
      :class="isConfigured ? 'bg-success/10 border border-success/20' : 'bg-surface-tertiary'"
    >
      <div class="flex items-center gap-3">
        <span :class="isConfigured ? 'text-success' : 'text-content-muted'" class="text-xl">
          {{ isConfigured ? '✓' : '🎌' }}
        </span>
        <div class="flex-1">
          <p class="font-medium" :class="isConfigured ? 'text-success' : 'text-content'">
            {{ isConfigured ? 'AniDB Connected' : 'Connect AniDB' }}
          </p>
          <p class="text-sm text-content-secondary">
            {{ isConfigured
              ? 'Your AniDB credentials are configured.'
              : 'Enter your AniDB username, password, and UDP client info.' }}
          </p>
        </div>
      </div>
    </div>

    <!-- Warning about rate limits -->
    <div class="p-4 rounded-lg bg-warning/10 border border-warning/20">
      <p class="text-warning font-medium flex items-center gap-2">
        <span>⚠️</span> AniDB Rate Limits
      </p>
      <p class="text-content-secondary text-sm mt-1">
        AniDB has strict rate limits on their UDP API. Kometa caches data to minimize requests,
        but initial runs may be slow. Be patient and don't run multiple instances simultaneously.
      </p>
    </div>

    <!-- Account Credentials -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <FormField
        label="Username"
        required
        tooltip="Your AniDB username"
      >
        <Input
          :model-value="props.modelValue.username || ''"
          placeholder="Your AniDB username"
          @update:model-value="updateField('username', $event)"
        />
      </FormField>

      <FormField
        label="Password"
        required
        tooltip="Your AniDB password"
      >
        <Input
          type="password"
          :model-value="props.modelValue.password || ''"
          placeholder="Your AniDB password"
          @update:model-value="updateField('password', $event)"
        />
      </FormField>
    </div>

    <!-- UDP Client Settings -->
    <div class="border-t border-border pt-6">
      <h4 class="font-medium mb-4 flex items-center gap-2">
        <span>🔧</span> UDP Client Settings
      </h4>
      <p class="text-sm text-content-secondary mb-4">
        AniDB requires a registered UDP API client. Register one at
        <a href="https://anidb.net/software/add" target="_blank" class="text-kometa-gold hover:underline">anidb.net/software/add</a>
      </p>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <FormField
          label="Client Name"
          required
          tooltip="Your registered UDP client name"
          help="Register at anidb.net/software/add"
        >
          <Input
            :model-value="props.modelValue.client || ''"
            placeholder="kometa"
            @update:model-value="updateField('client', $event)"
          />
        </FormField>

        <FormField
          label="Client Version"
          tooltip="Your UDP client version number"
          help="Default: 1"
        >
          <Input
            type="number"
            :model-value="String(props.modelValue.version || '')"
            placeholder="1"
            min="1"
            @update:model-value="updateField('version', $event ? Number($event) : undefined)"
          />
        </FormField>
      </div>
    </div>

    <!-- Additional Settings -->
    <div class="border-t border-border pt-6">
      <h4 class="font-medium mb-4 flex items-center gap-2">
        <span>⚙️</span> Additional Settings
      </h4>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <FormField
          label="Language"
          tooltip="Preferred language for anime titles"
        >
          <Select
            :model-value="props.modelValue.language || ''"
            :options="languageOptions"
            @update:model-value="updateField('language', $event || undefined)"
          />
        </FormField>

        <FormField
          label="Cache Expiration"
          tooltip="Number of days to cache AniDB data"
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
    </div>

    <!-- Test Connection -->
    <div v-if="isConfigured" class="flex items-center gap-4 p-4 rounded-lg bg-surface-tertiary">
      <button
        class="px-4 py-2 rounded-lg bg-kometa-gold text-black font-medium hover:bg-kometa-gold/90 transition-colors"
        @click="emit('test-connection')"
      >
        Test Connection
      </button>
      <span class="text-sm text-content-secondary">
        Verify your AniDB credentials
      </span>
    </div>

    <!-- Usage Examples -->
    <div class="border-t border-border pt-6">
      <h4 class="font-medium mb-4 flex items-center gap-2">
        <span>📚</span> AniDB Builders
      </h4>
      <p class="text-sm text-content-secondary mb-4">
        Once connected, you can use AniDB builders and data:
      </p>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
        <div class="p-3 rounded bg-surface-tertiary">
          <code class="text-kometa-gold">anidb_id</code>
          <p class="text-content-secondary mt-1">Build collections by AniDB ID</p>
        </div>
        <div class="p-3 rounded bg-surface-tertiary">
          <code class="text-kometa-gold">anidb_tag</code>
          <p class="text-content-secondary mt-1">Build collections by AniDB tags</p>
        </div>
        <div class="p-3 rounded bg-surface-tertiary">
          <code class="text-kometa-gold">anidb_relation</code>
          <p class="text-content-secondary mt-1">Group related anime together</p>
        </div>
        <div class="p-3 rounded bg-surface-tertiary">
          <code class="text-kometa-gold">mass_audience_rating_update: anidb</code>
          <p class="text-content-secondary mt-1">Use AniDB ratings</p>
        </div>
      </div>
    </div>
  </div>
</template>
