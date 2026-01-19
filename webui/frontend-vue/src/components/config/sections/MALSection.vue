<script setup lang="ts">
import { computed } from 'vue';
import FormField from '../FormField.vue';
import { Input } from '@/components/common';

interface MALConfig {
  client_id?: string;
  client_secret?: string;
  authorization?: {
    access_token?: string;
    token_type?: string;
    expires_in?: number;
    refresh_token?: string;
  };
}

interface Props {
  modelValue: MALConfig;
}

const props = defineProps<Props>();
const emit = defineEmits<{
  (e: 'update:modelValue', value: MALConfig): void;
}>();

function updateField<K extends keyof MALConfig>(field: K, value: MALConfig[K]) {
  emit('update:modelValue', { ...props.modelValue, [field]: value });
}

const isAuthorized = computed(() => !!props.modelValue.authorization?.access_token);
const hasCredentials = computed(() => !!props.modelValue.client_id && !!props.modelValue.client_secret);
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-start justify-between">
      <div>
        <div class="flex items-center gap-2">
          <span class="text-2xl">🎌</span>
          <h3 class="text-lg font-semibold">MyAnimeList Configuration</h3>
          <span class="text-xs px-2 py-0.5 rounded bg-surface-tertiary text-content-muted font-medium">Optional</span>
        </div>
        <p class="mt-1 text-sm text-content-secondary">
          Connect MyAnimeList for anime-focused collection builders and rankings.
        </p>
      </div>
      <a
        href="https://kometa.wiki/en/latest/config/myanimelist/"
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

    <!-- Authorization Status -->
    <div
      class="p-4 rounded-lg"
      :class="isAuthorized ? 'bg-success/10 border border-success/20' : 'bg-warning/10 border border-warning/20'"
    >
      <div class="flex items-center gap-3">
        <span :class="isAuthorized ? 'text-success' : 'text-warning'" class="text-xl">
          {{ isAuthorized ? '✓' : '⚠️' }}
        </span>
        <div class="flex-1">
          <p class="font-medium" :class="isAuthorized ? 'text-success' : 'text-warning'">
            {{ isAuthorized ? 'MyAnimeList Authorized' : 'MyAnimeList Not Authorized' }}
          </p>
          <p class="text-sm text-content-secondary">
            {{ isAuthorized
              ? 'Your MyAnimeList account is connected and ready to use.'
              : 'Enter your Client ID and Secret below, then authenticate.' }}
          </p>
        </div>
      </div>
    </div>

    <!-- API Credentials -->
    <div class="border-t border-border pt-6">
      <h4 class="font-medium mb-4 flex items-center gap-2">
        <span>🔑</span> API Credentials
      </h4>
      <p class="text-sm text-content-secondary mb-4">
        Create a MyAnimeList API application at
        <a
          href="https://myanimelist.net/apiconfig"
          target="_blank"
          class="text-kometa-gold hover:underline"
        >myanimelist.net/apiconfig</a>
        to get your credentials.
      </p>

      <div class="grid grid-cols-1 gap-4">
        <FormField
          label="Client ID"
          required
          tooltip="Your MyAnimeList API Client ID"
        >
          <Input
            :model-value="props.modelValue.client_id || ''"
            placeholder="Your MAL Client ID"
            @update:model-value="updateField('client_id', $event)"
          />
        </FormField>

        <FormField
          label="Client Secret"
          required
          tooltip="Your MyAnimeList API Client Secret"
        >
          <Input
            type="password"
            :model-value="props.modelValue.client_secret || ''"
            placeholder="Your MAL Client Secret"
            @update:model-value="updateField('client_secret', $event)"
          />
        </FormField>
      </div>
    </div>

    <!-- Authentication -->
    <div class="border-t border-border pt-6">
      <h4 class="font-medium mb-4 flex items-center gap-2">
        <span>🔐</span> Authentication
      </h4>

      <div class="space-y-4">
        <div class="p-4 rounded-lg bg-surface-tertiary">
          <h5 class="font-medium mb-2">How to Authenticate:</h5>
          <ol class="list-decimal list-inside space-y-2 text-sm text-content-secondary">
            <li>Register an API application at myanimelist.net/apiconfig</li>
            <li>Set the App Redirect URL to: <code class="text-kometa-gold">http://localhost/</code></li>
            <li>Enter your Client ID and Client Secret above</li>
            <li>Save your configuration</li>
            <li>Run Kometa - it will open a browser for MAL authorization</li>
            <li>Authorize the app and Kometa will save the tokens</li>
          </ol>
        </div>

        <div v-if="isAuthorized" class="p-3 rounded-lg bg-surface-tertiary text-sm">
          <p class="text-content-muted">
            Authorization stored. Token will be automatically refreshed when needed.
          </p>
        </div>
      </div>
    </div>

    <!-- Usage Examples -->
    <div class="border-t border-border pt-6">
      <h4 class="font-medium mb-4 flex items-center gap-2">
        <span>📚</span> MAL Builders
      </h4>
      <p class="text-sm text-content-secondary mb-4">
        Once authorized, you can use these MyAnimeList builders in your collection files:
      </p>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
        <div class="p-3 rounded bg-surface-tertiary">
          <code class="text-kometa-gold">mal_all</code>
          <p class="text-content-secondary mt-1">All anime from your MAL list</p>
        </div>
        <div class="p-3 rounded bg-surface-tertiary">
          <code class="text-kometa-gold">mal_airing</code>
          <p class="text-content-secondary mt-1">Currently airing anime</p>
        </div>
        <div class="p-3 rounded bg-surface-tertiary">
          <code class="text-kometa-gold">mal_season</code>
          <p class="text-content-secondary mt-1">Anime from a specific season</p>
        </div>
        <div class="p-3 rounded bg-surface-tertiary">
          <code class="text-kometa-gold">mal_suggested</code>
          <p class="text-content-secondary mt-1">MAL's personalized suggestions</p>
        </div>
        <div class="p-3 rounded bg-surface-tertiary">
          <code class="text-kometa-gold">mal_userlist</code>
          <p class="text-content-secondary mt-1">Anime from any user's list</p>
        </div>
        <div class="p-3 rounded bg-surface-tertiary">
          <code class="text-kometa-gold">mal_top_airing</code>
          <p class="text-content-secondary mt-1">Top rated airing anime</p>
        </div>
      </div>
    </div>
  </div>
</template>
