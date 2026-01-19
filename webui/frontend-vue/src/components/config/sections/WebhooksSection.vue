<script setup lang="ts">
import { ref } from 'vue';
import FormField from '../FormField.vue';
import { Input, Checkbox, Select } from '@/components/common';

interface WebhookEntry {
  id: string;
  name: string;
  url: string;
  run_start?: boolean;
  run_end?: boolean;
  collection_changes?: boolean;
  errors?: boolean;
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

function addWebhook() {
  const newWebhook: WebhookEntry = {
    id: crypto.randomUUID(),
    name: 'New Webhook',
    url: '',
    run_start: false,
    run_end: true,
    collection_changes: false,
    errors: true,
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

    <!-- Webhooks List -->
    <div v-if="getWebhooks().length > 0 && !editingWebhook" class="space-y-3">
      <div
        v-for="webhook in getWebhooks()"
        :key="webhook.id"
        class="p-4 rounded-lg bg-surface-secondary border border-border hover:border-kometa-gold/30 transition-colors"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2">
              <span class="font-medium">{{ webhook.name }}</span>
              <div class="flex gap-1">
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

        <div class="border-t border-border pt-4">
          <p class="text-sm font-medium mb-3">Notification Events</p>
          <div class="space-y-2">
            <Checkbox v-model="editingWebhook.run_start">
              <span class="font-medium">Run Start</span>
              <span class="text-content-secondary ml-2">Notify when Kometa starts running</span>
            </Checkbox>

            <Checkbox v-model="editingWebhook.run_end">
              <span class="font-medium">Run End</span>
              <span class="text-content-secondary ml-2">Notify when Kometa finishes running</span>
            </Checkbox>

            <Checkbox v-model="editingWebhook.collection_changes">
              <span class="font-medium">Collection Changes</span>
              <span class="text-content-secondary ml-2">Notify when collections are updated</span>
            </Checkbox>

            <Checkbox v-model="editingWebhook.errors">
              <span class="font-medium">Errors</span>
              <span class="text-content-secondary ml-2">Notify when errors occur</span>
            </Checkbox>
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
