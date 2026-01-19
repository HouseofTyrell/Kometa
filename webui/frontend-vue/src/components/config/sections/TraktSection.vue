<script setup lang="ts">
import { computed } from 'vue';
import FormField from '../FormField.vue';
import SectionHeader from '../SectionHeader.vue';
import { Input, Checkbox } from '@/components/common';
import { useConfigSection } from '@/composables';

interface TraktConfig {
  client_id?: string;
  client_secret?: string;
  pin?: string;
  authorization?: {
    access_token?: string;
    token_type?: string;
    expires_in?: number;
    refresh_token?: string;
    scope?: string;
    created_at?: number;
  };
}

interface Props {
  modelValue: TraktConfig;
}

const props = defineProps<Props>();
const emit = defineEmits<{
  (e: 'update:modelValue', value: TraktConfig): void;
  (e: 'authenticate'): void;
}>();

const { updateField } = useConfigSection<TraktConfig>(props, emit);

const isAuthorized = computed(() => !!props.modelValue.authorization?.access_token);
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <SectionHeader
      icon="📋"
      title="Trakt Configuration"
      description="Connect Trakt for user lists, watched status, and collection builders."
      docs-url="https://kometa.wiki/en/latest/config/trakt/"
      optional
    />

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
            {{ isAuthorized ? 'Trakt Authorized' : 'Trakt Not Authorized' }}
          </p>
          <p class="text-sm text-content-secondary">
            {{ isAuthorized
              ? 'Your Trakt account is connected and ready to use.'
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
        Create a Trakt API application at
        <a
          href="https://trakt.tv/oauth/applications"
          target="_blank"
          class="text-kometa-gold hover:underline"
        >trakt.tv/oauth/applications</a>
        to get your credentials.
      </p>

      <div class="grid grid-cols-1 gap-4">
        <FormField
          label="Client ID"
          required
          tooltip="Your Trakt API Client ID"
        >
          <Input
            :model-value="props.modelValue.client_id || ''"
            placeholder="Your Trakt Client ID"
            @update:model-value="updateField('client_id', $event)"
          />
        </FormField>

        <FormField
          label="Client Secret"
          required
          tooltip="Your Trakt API Client Secret"
        >
          <Input
            type="password"
            :model-value="props.modelValue.client_secret || ''"
            placeholder="Your Trakt Client Secret"
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
            <li>Enter your Client ID and Client Secret above</li>
            <li>Save your configuration</li>
            <li>Run Kometa - it will display a PIN and URL</li>
            <li>Visit the URL and enter the PIN to authorize</li>
            <li>Kometa will automatically save the authorization tokens</li>
          </ol>
        </div>

        <FormField
          label="PIN (Optional)"
          tooltip="Manual PIN entry if needed"
          help="Usually not needed - Kometa handles this automatically"
        >
          <Input
            :model-value="props.modelValue.pin || ''"
            placeholder="PIN from Trakt (if required)"
            @update:model-value="updateField('pin', $event)"
          />
        </FormField>

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
        <span>📚</span> Trakt Builders
      </h4>
      <p class="text-sm text-content-secondary mb-4">
        Once authorized, you can use these Trakt builders in your collection files:
      </p>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
        <div class="p-3 rounded bg-surface-tertiary">
          <code class="text-kometa-gold">trakt_list</code>
          <p class="text-content-secondary mt-1">Build from any Trakt list</p>
        </div>
        <div class="p-3 rounded bg-surface-tertiary">
          <code class="text-kometa-gold">trakt_watchlist</code>
          <p class="text-content-secondary mt-1">Build from user's watchlist</p>
        </div>
        <div class="p-3 rounded bg-surface-tertiary">
          <code class="text-kometa-gold">trakt_trending</code>
          <p class="text-content-secondary mt-1">Trending movies/shows</p>
        </div>
        <div class="p-3 rounded bg-surface-tertiary">
          <code class="text-kometa-gold">trakt_popular</code>
          <p class="text-content-secondary mt-1">Most popular items</p>
        </div>
        <div class="p-3 rounded bg-surface-tertiary">
          <code class="text-kometa-gold">trakt_collected</code>
          <p class="text-content-secondary mt-1">User's collected items</p>
        </div>
        <div class="p-3 rounded bg-surface-tertiary">
          <code class="text-kometa-gold">trakt_recommended</code>
          <p class="text-content-secondary mt-1">Personalized recommendations</p>
        </div>
      </div>
    </div>
  </div>
</template>
