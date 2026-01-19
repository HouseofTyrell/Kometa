<script setup lang="ts">
import { computed } from 'vue';
import FormField from '../FormField.vue';
import { Input } from '@/components/common';

interface GitHubConfig {
  token?: string;
}

interface Props {
  modelValue: GitHubConfig;
}

const props = defineProps<Props>();
const emit = defineEmits<{
  (e: 'update:modelValue', value: GitHubConfig): void;
}>();

function updateField<K extends keyof GitHubConfig>(field: K, value: GitHubConfig[K]) {
  emit('update:modelValue', { ...props.modelValue, [field]: value });
}

const hasToken = computed(() => !!props.modelValue.token);
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-start justify-between">
      <div>
        <div class="flex items-center gap-2">
          <span class="text-2xl">🐙</span>
          <h3 class="text-lg font-semibold">GitHub Configuration</h3>
          <span class="text-xs px-2 py-0.5 rounded bg-surface-tertiary text-content-muted font-medium">Optional</span>
        </div>
        <p class="mt-1 text-sm text-content-secondary">
          Configure a GitHub Personal Access Token to access private repositories for collection files.
        </p>
      </div>
      <a
        href="https://kometa.wiki/en/latest/config/github/"
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
      :class="hasToken ? 'bg-success/10 border border-success/20' : 'bg-surface-tertiary'"
    >
      <div class="flex items-center gap-3">
        <span :class="hasToken ? 'text-success' : 'text-content-muted'" class="text-xl">
          {{ hasToken ? '✓' : '🐙' }}
        </span>
        <div class="flex-1">
          <p class="font-medium" :class="hasToken ? 'text-success' : 'text-content'">
            {{ hasToken ? 'GitHub Token Configured' : 'Configure GitHub Token' }}
          </p>
          <p class="text-sm text-content-secondary">
            {{ hasToken
              ? 'Your GitHub Personal Access Token is configured.'
              : 'Add a token to access private repositories and avoid rate limits.' }}
          </p>
        </div>
      </div>
    </div>

    <!-- Token Input -->
    <FormField
      label="Personal Access Token"
      tooltip="GitHub Personal Access Token with repo access"
      help="Create a token at github.com/settings/tokens"
    >
      <Input
        type="password"
        :model-value="props.modelValue.token || ''"
        placeholder="ghp_xxxxxxxxxxxxxxxxxxxx"
        @update:model-value="updateField('token', $event)"
      />
    </FormField>

    <!-- Usage Examples -->
    <div class="border-t border-border pt-6">
      <h4 class="font-medium mb-4 flex items-center gap-2">
        <span>📚</span> Using GitHub Files
      </h4>
      <p class="text-sm text-content-secondary mb-4">
        With a GitHub token, you can reference collection files from repositories:
      </p>

      <div class="space-y-3 text-sm">
        <div class="p-3 rounded bg-surface-tertiary font-mono">
          <p class="text-content-muted mb-1"># Public repository</p>
          <p class="text-kometa-gold">- git://username/repo/path/to/file.yml</p>
        </div>
        <div class="p-3 rounded bg-surface-tertiary font-mono">
          <p class="text-content-muted mb-1"># Private repository (requires token)</p>
          <p class="text-kometa-gold">- git://username/private-repo/collections.yml</p>
        </div>
      </div>
    </div>

    <!-- Token Permissions -->
    <div class="border-t border-border pt-6">
      <h4 class="font-medium mb-4 flex items-center gap-2">
        <span>🔐</span> Required Token Permissions
      </h4>
      <div class="p-4 rounded-lg bg-surface-tertiary text-sm">
        <p class="text-content-secondary mb-3">
          Your Personal Access Token needs these permissions:
        </p>
        <ul class="list-disc list-inside space-y-1 text-content-secondary">
          <li><code class="text-kometa-gold">repo</code> - Full control of private repositories (for private repos)</li>
          <li><code class="text-kometa-gold">public_repo</code> - Access public repositories only (for public repos)</li>
        </ul>
        <div class="mt-4 p-3 rounded bg-warning/10 border border-warning/20">
          <p class="text-warning font-medium flex items-center gap-2">
            <span>⚠️</span> Security Note
          </p>
          <p class="text-content-secondary mt-1">
            Keep your token secure. Never share it or commit it to public repositories.
            Consider using a fine-grained token with minimal permissions.
          </p>
        </div>
      </div>
    </div>

    <!-- How to Create Token -->
    <div class="border-t border-border pt-6">
      <h4 class="font-medium mb-4 flex items-center gap-2">
        <span>💡</span> Creating a Personal Access Token
      </h4>
      <div class="p-4 rounded-lg bg-surface-tertiary text-sm">
        <ol class="list-decimal list-inside space-y-2 text-content-secondary">
          <li>Go to GitHub Settings → Developer Settings → Personal Access Tokens</li>
          <li>Click "Generate new token" (classic or fine-grained)</li>
          <li>Give it a descriptive name like "Kometa"</li>
          <li>Select the required scopes (repo or public_repo)</li>
          <li>Click "Generate token" and copy it immediately</li>
        </ol>
        <p class="mt-3">
          <a
            href="https://github.com/settings/tokens"
            target="_blank"
            class="text-kometa-gold hover:underline"
          >
            Create a token on GitHub →
          </a>
        </p>
      </div>
    </div>
  </div>
</template>
