<script setup lang="ts">
import { computed } from 'vue';
import { Card, Badge, Spinner } from '@/components/common';
import { useRunDiff, type DryRunDiffResponse } from '@/api';

interface Props {
  runId: string;
}

const props = defineProps<Props>();

const { data: diff, isLoading, isError, error } = useRunDiff(props.runId);

// Operation type labels and colors
const operationLabels: Record<string, { label: string; color: string }> = {
  edit_metadata: { label: 'Metadata Edit', color: 'text-info' },
  upload_poster: { label: 'Poster Upload', color: 'text-purple-400' },
  upload_background: { label: 'Background Upload', color: 'text-purple-400' },
  playlist_add_items: { label: 'Collection Add', color: 'text-success' },
  playlist_remove_items: { label: 'Collection Remove', color: 'text-error' },
  collection_add: { label: 'Items Added', color: 'text-success' },
  collection_remove: { label: 'Items Removed', color: 'text-error' },
  create_collection: { label: 'Collection Create', color: 'text-kometa-gold' },
  delete_collection: { label: 'Collection Delete', color: 'text-error' },
};

const getOperationInfo = (op: string) => {
  return operationLabels[op] || { label: op.replace(/_/g, ' '), color: 'text-content-secondary' };
};

// Sort operations by count
const sortedOperations = computed(() => {
  if (!diff.value?.summary?.operations_by_type) return [];
  return Object.entries(diff.value.summary.operations_by_type)
    .sort((a, b) => b[1] - a[1]);
});
</script>

<template>
  <div class="space-y-4">
    <!-- Loading State -->
    <div v-if="isLoading" class="flex items-center justify-center py-12">
      <Spinner size="lg" />
      <span class="ml-3 text-content-secondary">Analyzing dry run changes...</span>
    </div>

    <!-- Error State -->
    <div v-else-if="isError" class="p-4 rounded-lg bg-error/10 border border-error/20">
      <p class="text-error">Failed to load diff: {{ error?.message || 'Unknown error' }}</p>
    </div>

    <!-- Not a dry run -->
    <div v-else-if="diff && !diff.is_dry_run" class="p-4 rounded-lg bg-surface-tertiary">
      <p class="text-content-secondary">
        <span class="text-xl mr-2">ℹ️</span>
        {{ diff.message || 'This run was not a dry run - diff preview is only available for dry runs.' }}
      </p>
    </div>

    <!-- Diff Content -->
    <template v-else-if="diff?.summary">
      <!-- Summary Card -->
      <Card class="bg-surface-secondary">
        <div class="flex items-center gap-3 mb-4">
          <div class="w-10 h-10 rounded-lg bg-kometa-gold/10 flex items-center justify-center text-xl">
            📊
          </div>
          <div>
            <h3 class="font-semibold">Dry Run Summary</h3>
            <p class="text-sm text-content-secondary">
              Changes that would be applied if run in apply mode
            </p>
          </div>
        </div>

        <!-- Stats Grid -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div class="p-4 rounded-lg bg-surface-tertiary text-center">
            <p class="text-3xl font-bold text-kometa-gold">{{ diff.summary.total_operations }}</p>
            <p class="text-sm text-content-secondary">Total Operations</p>
          </div>
          <div class="p-4 rounded-lg bg-success/10 text-center">
            <p class="text-3xl font-bold text-success">+{{ diff.summary.total_added }}</p>
            <p class="text-sm text-content-secondary">Items Added</p>
          </div>
          <div class="p-4 rounded-lg bg-error/10 text-center">
            <p class="text-3xl font-bold text-error">-{{ diff.summary.total_removed }}</p>
            <p class="text-sm text-content-secondary">Items Removed</p>
          </div>
          <div class="p-4 rounded-lg bg-info/10 text-center">
            <p class="text-3xl font-bold text-info">{{ diff.summary.total_updated }}</p>
            <p class="text-sm text-content-secondary">Items Updated</p>
          </div>
        </div>
      </Card>

      <!-- Operations Breakdown -->
      <Card v-if="sortedOperations.length > 0">
        <h4 class="font-semibold mb-4 flex items-center gap-2">
          <span>⚙️</span> Operations by Type
        </h4>
        <div class="space-y-2">
          <div
            v-for="[operation, count] in sortedOperations"
            :key="operation"
            class="flex items-center gap-3 p-2 rounded bg-surface-tertiary"
          >
            <div class="flex-1">
              <span :class="getOperationInfo(operation).color" class="font-medium">
                {{ getOperationInfo(operation).label }}
              </span>
            </div>
            <Badge variant="default">{{ count }}</Badge>
          </div>
        </div>
      </Card>

      <!-- Collections Affected -->
      <Card v-if="diff.collections && diff.collections.length > 0">
        <h4 class="font-semibold mb-4 flex items-center gap-2">
          <span>📚</span> Collections Affected
          <Badge variant="default" size="sm">{{ diff.summary.collections_affected }}</Badge>
        </h4>
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="text-left text-content-secondary border-b border-border">
              <tr>
                <th class="pb-2 font-medium">Collection</th>
                <th class="pb-2 font-medium text-center text-success">Added</th>
                <th class="pb-2 font-medium text-center text-error">Removed</th>
                <th class="pb-2 font-medium text-center text-info">Updated</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-border/50">
              <tr
                v-for="collection in diff.collections"
                :key="collection.name"
                class="hover:bg-surface-tertiary/50"
              >
                <td class="py-2 font-medium">{{ collection.name }}</td>
                <td class="py-2 text-center">
                  <span v-if="collection.items_added" class="text-success font-medium">
                    +{{ collection.items_added }}
                  </span>
                  <span v-else class="text-content-muted">-</span>
                </td>
                <td class="py-2 text-center">
                  <span v-if="collection.items_removed" class="text-error font-medium">
                    -{{ collection.items_removed }}
                  </span>
                  <span v-else class="text-content-muted">-</span>
                </td>
                <td class="py-2 text-center">
                  <span v-if="collection.items_updated" class="text-info font-medium">
                    {{ collection.items_updated }}
                  </span>
                  <span v-else class="text-content-muted">-</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </Card>

      <!-- Sample Operations -->
      <Card v-if="diff.operations && diff.operations.length > 0">
        <h4 class="font-semibold mb-4 flex items-center gap-2">
          <span>📝</span> Sample Operations
          <span class="text-xs text-content-muted font-normal">
            (showing first {{ diff.operations.length }} of {{ diff.summary.total_operations }})
          </span>
        </h4>
        <div class="space-y-2 max-h-96 overflow-auto">
          <div
            v-for="(op, index) in diff.operations"
            :key="index"
            class="p-3 rounded bg-surface-tertiary font-mono text-xs"
          >
            <span :class="getOperationInfo(op.operation).color" class="font-semibold">
              {{ op.operation }}
            </span>
            <span v-if="op.target" class="text-content-secondary"> on </span>
            <span v-if="op.target" class="text-kometa-gold">"{{ op.target }}"</span>
            <span v-if="op.details" class="text-content-muted block mt-1">{{ op.details }}</span>
          </div>
        </div>
      </Card>

      <!-- Empty State -->
      <div v-if="diff.summary.total_operations === 0" class="p-8 text-center text-content-muted">
        <span class="text-4xl block mb-4">✅</span>
        <p class="text-lg font-medium">No changes detected</p>
        <p class="text-sm mt-2">The dry run completed without any pending changes.</p>
      </div>
    </template>
  </div>
</template>
