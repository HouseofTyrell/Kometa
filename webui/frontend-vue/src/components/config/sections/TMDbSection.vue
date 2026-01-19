<script setup lang="ts">
import FormField from '../FormField.vue';
import SectionHeader from '../SectionHeader.vue';
import TestConnectionButton from '../TestConnectionButton.vue';
import { Input, Select } from '@/components/common';
import { useConfigSection } from '@/composables';

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

const { config, updateField } = useConfigSection<TMDbConfig>(props, emit);

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
    <SectionHeader
      icon="🎬"
      title="TMDb Configuration"
      description="Configure The Movie Database (TMDb) API for metadata, images, and collection builders."
      docs-url="https://kometa.wiki/en/latest/config/tmdb/"
      required
    />

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
    <TestConnectionButton
      description="Verify your TMDb API key is valid"
      @test="emit('test-connection')"
    />
  </div>
</template>
