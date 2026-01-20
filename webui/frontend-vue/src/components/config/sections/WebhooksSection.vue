<script setup lang="ts">
import { ref, computed } from 'vue';
import FormField from '../FormField.vue';
import { Input, Checkbox, Select } from '@/components/common';
import { useTestWebhook } from '@/api/media';

type WebhookServiceType = 'discord' | 'slack' | 'teams' | 'custom';

interface WebhookEntry {
  id: string;
  name: string;
  url: string;
  service_type?: WebhookServiceType;
  // Run events
  run_start?: boolean;
  run_end?: boolean;
  // Collection events
  collection_changes?: boolean;
  collection_created?: boolean;
  collection_updated?: boolean;
  collection_deleted?: boolean;
  // Playlist events
  playlist_changes?: boolean;
  // Overlay events
  overlay_changes?: boolean;
  // Library events
  library_changes?: boolean;
  // Error events
  errors?: boolean;
  // Version check
  version_update?: boolean;
}

interface WebhooksConfig {
  webhooks?: WebhookEntry[];
}

interface Props {
  modelValue: WebhooksConfig;
}

const props = defineProps<Props>();
const emit = defineEmits<{
  (e: 'update:modelValue', value: WebhooksConfig): void;
}>();

const editingWebhook = ref<WebhookEntry | null>(null);

function getWebhooks(): WebhookEntry[] {
  return props.modelValue.webhooks || [];
}

// Service type options
const serviceTypeOptions = [
  { value: 'discord', label: 'Discord' },
  { value: 'slack', label: 'Slack' },
  { value: 'teams', label: 'Microsoft Teams' },
  { value: 'custom', label: 'Custom / Other' },
];

function addWebhook() {
  const newWebhook: WebhookEntry = {
    id: crypto.randomUUID(),
    name: 'New Webhook',
    url: '',
    service_type: 'discord',
    run_start: false,
    run_end: true,
    collection_changes: false,
    collection_created: false,
    collection_updated: false,
    collection_deleted: false,
    playlist_changes: false,
    overlay_changes: false,
    library_changes: false,
    errors: true,
    version_update: false,
  };
  editingWebhook.value = newWebhook;
}

function saveWebhook() {
  if (!editingWebhook.value) return;

  const webhooks = getWebhooks();
  const existingIndex = webhooks.findIndex((w) => w.id === editingWebhook.value!.id);

  if (existingIndex >= 0) {
    webhooks[existingIndex] = editingWebhook.value;
  } else {
    webhooks.push(editingWebhook.value);
  }

  emit('update:modelValue', { ...props.modelValue, webhooks });
  editingWebhook.value = null;
}

function editWebhook(webhook: WebhookEntry) {
  editingWebhook.value = { ...webhook };
}

function deleteWebhook(id: string) {
  const webhooks = getWebhooks().filter((w) => w.id !== id);
  emit('update:modelValue', { ...props.modelValue, webhooks });
}

function cancelEdit() {
  editingWebhook.value = null;
}

// Webhook testing
const testWebhookMutation = useTestWebhook();
const testingWebhookId = ref<string | null>(null);
const testResult = ref<{ success: boolean; message: string } | null>(null);

const isTestingWebhook = computed(() => testWebhookMutation.isPending.value);

async function testWebhook(webhook: WebhookEntry) {
  if (!webhook.url) {
    testResult.value = { success: false, message: 'No URL configured' };
    return;
  }

  testingWebhookId.value = webhook.id;
  testResult.value = null;

  try {
    const result = await testWebhookMutation.mutateAsync({
      url: webhook.url,
      service: webhook.service_type || 'custom',
      event: 'test',
    });
    testResult.value = {
      success: result.success,
      message: result.success ? (result.message || 'Test successful!') : (result.error || 'Test failed'),
    };
  } catch (err) {
    testResult.value = {
      success: false,
      message: err instanceof Error ? err.message : 'Test failed',
    };
  } finally {
    testingWebhookId.value = null;
  }
}

function clearTestResult() {
  testResult.value = null;
}
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-start justify-between">
      <div>
        <div class="flex items-center gap-2">
          <span class="text-2xl">🔗</span>
          <h3 class="text-lg font-semibold">Webhooks Configuration</h3>
          <span class="text-xs px-2 py-0.5 rounded bg-surface-tertiary text-content-muted font-medium">Optional</span>
        </div>
        <p class="mt-1 text-sm text-content-secondary">
          Configure custom webhooks to receive Kometa notifications in Discord, Slack, or any webhook-compatible service.
        </p>
      </div>
      <a
        href="https://kometa.wiki/en/latest/config/webhooks/"
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

    <!-- Test Result Banner -->
    <div
      v-if="testResult"
      :class="[
        'p-3 rounded-lg flex items-center justify-between',
        testResult.success ? 'bg-green-500/20 border border-green-500/30' : 'bg-red-500/20 border border-red-500/30'
      ]"
    >
      <div class="flex items-center gap-2">
        <svg v-if="testResult.success" class="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
        </svg>
        <svg v-else class="w-5 h-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
        <span :class="testResult.success ? 'text-green-400' : 'text-red-400'">
          {{ testResult.message }}
        </span>
      </div>
      <button
        class="p-1 rounded hover:bg-white/10 transition-colors"
        @click="clearTestResult"
      >
        <svg class="w-4 h-4 text-content-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>

    <!-- Webhooks List -->
    <div v-if="getWebhooks().length > 0 && !editingWebhook" class="space-y-3">
      <div
        v-for="webhook in getWebhooks()"
        :key="webhook.id"
        class="p-4 rounded-lg bg-surface-secondary border border-border hover:border-kometa-gold/30 transition-colors"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 flex-wrap">
              <span class="font-medium">{{ webhook.name }}</span>
              <span
                v-if="webhook.service_type"
                class="text-xs px-1.5 py-0.5 rounded bg-purple-500/20 text-purple-400"
              >
                {{ serviceTypeOptions.find(s => s.value === webhook.service_type)?.label || webhook.service_type }}
              </span>
              <div class="flex gap-1 flex-wrap">
                <span
                  v-if="webhook.run_start"
                  class="text-xs px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-400"
                >
                  Start
                </span>
                <span
                  v-if="webhook.run_end"
                  class="text-xs px-1.5 py-0.5 rounded bg-green-500/20 text-green-400"
                >
                  End
                </span>
                <span
                  v-if="webhook.collection_changes || webhook.collection_created || webhook.collection_updated || webhook.collection_deleted"
                  class="text-xs px-1.5 py-0.5 rounded bg-yellow-500/20 text-yellow-400"
                >
                  Collections
                </span>
                <span
                  v-if="webhook.playlist_changes"
                  class="text-xs px-1.5 py-0.5 rounded bg-cyan-500/20 text-cyan-400"
                >
                  Playlists
                </span>
                <span
                  v-if="webhook.overlay_changes"
                  class="text-xs px-1.5 py-0.5 rounded bg-orange-500/20 text-orange-400"
                >
                  Overlays
                </span>
                <span
                  v-if="webhook.errors"
                  class="text-xs px-1.5 py-0.5 rounded bg-red-500/20 text-red-400"
                >
                  Errors
                </span>
              </div>
            </div>
            <p class="text-sm text-content-muted truncate mt-1">
              {{ webhook.url || 'No URL configured' }}
            </p>
          </div>
          <div class="flex items-center gap-2 ml-4">
            <button
              class="p-1.5 rounded hover:bg-kometa-gold/20 text-content-secondary hover:text-kometa-gold transition-colors disabled:opacity-50"
              title="Test webhook"
              :disabled="isTestingWebhook && testingWebhookId === webhook.id"
              @click="testWebhook(webhook)"
            >
              <svg v-if="isTestingWebhook && testingWebhookId === webhook.id" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M5 3l14 9-14 9V3z" />
              </svg>
            </button>
            <button
              class="p-1.5 rounded hover:bg-surface-tertiary text-content-secondary hover:text-content transition-colors"
              title="Edit webhook"
              @click="editWebhook(webhook)"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </button>
            <button
              class="p-1.5 rounded hover:bg-error/20 text-content-secondary hover:text-error transition-colors"
              title="Delete webhook"
              @click="deleteWebhook(webhook.id)"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div
      v-else-if="!editingWebhook"
      class="p-8 rounded-lg bg-surface-tertiary text-center"
    >
      <span class="text-4xl mb-4 block">🔗</span>
      <p class="text-content-secondary mb-4">
        No webhooks configured yet. Add a webhook to receive notifications.
      </p>
    </div>

    <!-- Add Webhook Button -->
    <button
      v-if="!editingWebhook"
      class="w-full p-4 rounded-lg border-2 border-dashed border-border hover:border-kometa-gold/50 hover:bg-surface-tertiary/50 transition-colors text-content-secondary hover:text-content flex items-center justify-center gap-2"
      @click="addWebhook"
    >
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
      </svg>
      Add Webhook
    </button>

    <!-- Webhook Editor -->
    <div v-if="editingWebhook" class="p-4 rounded-lg bg-surface-secondary border border-kometa-gold/30">
      <h4 class="font-medium mb-4 flex items-center gap-2">
        <span>✏️</span>
        {{ getWebhooks().some((w) => w.id === editingWebhook.id) ? 'Edit Webhook' : 'New Webhook' }}
      </h4>

      <div class="space-y-4">
        <FormField
          label="Webhook Name"
          required
          tooltip="A friendly name to identify this webhook"
        >
          <Input
            v-model="editingWebhook.name"
            placeholder="e.g., Discord Notifications"
          />
        </FormField>

        <FormField
          label="Webhook URL"
          required
          tooltip="The full webhook URL from your notification service"
          help="Discord: Server Settings > Integrations > Webhooks"
        >
          <Input
            v-model="editingWebhook.url"
            placeholder="https://discord.com/api/webhooks/..."
          />
        </FormField>

        <FormField
          label="Service Type"
          tooltip="Select the service type for proper message formatting"
        >
          <Select
            v-model="editingWebhook.service_type"
            :options="serviceTypeOptions"
          />
        </FormField>

        <div class="border-t border-border pt-4">
          <p class="text-sm font-medium mb-3">Notification Events</p>

          <!-- Run Events -->
          <div class="mb-4">
            <p class="text-xs text-content-muted uppercase tracking-wide mb-2">Run Events</p>
            <div class="space-y-2 pl-2">
              <Checkbox v-model="editingWebhook.run_start">
                <span class="font-medium">Run Start</span>
                <span class="text-content-secondary ml-2">Notify when Kometa starts running</span>
              </Checkbox>

              <Checkbox v-model="editingWebhook.run_end">
                <span class="font-medium">Run End</span>
                <span class="text-content-secondary ml-2">Notify when Kometa finishes running</span>
              </Checkbox>
            </div>
          </div>

          <!-- Collection Events -->
          <div class="mb-4">
            <p class="text-xs text-content-muted uppercase tracking-wide mb-2">Collection Events</p>
            <div class="space-y-2 pl-2">
              <Checkbox v-model="editingWebhook.collection_changes">
                <span class="font-medium">All Collection Changes</span>
                <span class="text-content-secondary ml-2">Notify on any collection modification</span>
              </Checkbox>

              <Checkbox v-model="editingWebhook.collection_created">
                <span class="font-medium">Collection Created</span>
                <span class="text-content-secondary ml-2">Notify when new collections are created</span>
              </Checkbox>

              <Checkbox v-model="editingWebhook.collection_updated">
                <span class="font-medium">Collection Updated</span>
                <span class="text-content-secondary ml-2">Notify when collections are modified</span>
              </Checkbox>

              <Checkbox v-model="editingWebhook.collection_deleted">
                <span class="font-medium">Collection Deleted</span>
                <span class="text-content-secondary ml-2">Notify when collections are removed</span>
              </Checkbox>
            </div>
          </div>

          <!-- Media Events -->
          <div class="mb-4">
            <p class="text-xs text-content-muted uppercase tracking-wide mb-2">Media Events</p>
            <div class="space-y-2 pl-2">
              <Checkbox v-model="editingWebhook.playlist_changes">
                <span class="font-medium">Playlist Changes</span>
                <span class="text-content-secondary ml-2">Notify when playlists are updated</span>
              </Checkbox>

              <Checkbox v-model="editingWebhook.overlay_changes">
                <span class="font-medium">Overlay Changes</span>
                <span class="text-content-secondary ml-2">Notify when overlays are applied</span>
              </Checkbox>

              <Checkbox v-model="editingWebhook.library_changes">
                <span class="font-medium">Library Changes</span>
                <span class="text-content-secondary ml-2">Notify on library operations</span>
              </Checkbox>
            </div>
          </div>

          <!-- System Events -->
          <div>
            <p class="text-xs text-content-muted uppercase tracking-wide mb-2">System Events</p>
            <div class="space-y-2 pl-2">
              <Checkbox v-model="editingWebhook.errors">
                <span class="font-medium">Errors</span>
                <span class="text-content-secondary ml-2">Notify when errors occur</span>
              </Checkbox>

              <Checkbox v-model="editingWebhook.version_update">
                <span class="font-medium">Version Updates</span>
                <span class="text-content-secondary ml-2">Notify when new Kometa versions are available</span>
              </Checkbox>
            </div>
          </div>
        </div>

        <div class="flex items-center gap-3 pt-4 border-t border-border">
          <button
            class="px-4 py-2 rounded-lg bg-kometa-gold text-black font-medium hover:bg-kometa-gold/90 transition-colors"
            @click="saveWebhook"
          >
            Save Webhook
          </button>
          <button
            class="px-4 py-2 rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center gap-2"
            :disabled="!editingWebhook.url || isTestingWebhook"
            @click="testWebhook(editingWebhook)"
          >
            <svg v-if="isTestingWebhook && testingWebhookId === editingWebhook.id" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Test Webhook
          </button>
          <button
            class="px-4 py-2 rounded-lg bg-surface-tertiary text-content hover:bg-surface-tertiary/80 transition-colors"
            @click="cancelEdit"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>

    <!-- Webhook Templates -->
    <div class="border-t border-border pt-6">
      <h4 class="font-medium mb-4 flex items-center gap-2">
        <span>📚</span> Supported Services
      </h4>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
        <div class="p-3 rounded bg-surface-tertiary">
          <div class="flex items-center gap-2 mb-1">
            <span>💬</span>
            <span class="font-medium">Discord</span>
          </div>
          <p class="text-content-secondary">Server Settings → Integrations → Webhooks</p>
        </div>
        <div class="p-3 rounded bg-surface-tertiary">
          <div class="flex items-center gap-2 mb-1">
            <span>💼</span>
            <span class="font-medium">Slack</span>
          </div>
          <p class="text-content-secondary">Apps → Incoming Webhooks</p>
        </div>
        <div class="p-3 rounded bg-surface-tertiary">
          <div class="flex items-center gap-2 mb-1">
            <span>🤖</span>
            <span class="font-medium">Telegram</span>
          </div>
          <p class="text-content-secondary">Use a webhook-to-Telegram bridge</p>
        </div>
        <div class="p-3 rounded bg-surface-tertiary">
          <div class="flex items-center gap-2 mb-1">
            <span>🔧</span>
            <span class="font-medium">Custom</span>
          </div>
          <p class="text-content-secondary">Any service accepting HTTP POST</p>
        </div>
      </div>
    </div>
  </div>
</template>
