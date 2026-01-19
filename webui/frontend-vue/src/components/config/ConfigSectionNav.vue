<script setup lang="ts">
import { computed } from 'vue';

export interface ConfigSection {
  id: string;
  label: string;
  icon: string;
  group: string;
  required?: boolean;
}

interface Props {
  sections: ConfigSection[];
  activeSection: string;
}

const props = defineProps<Props>();
const emit = defineEmits<{
  (e: 'select', sectionId: string): void;
}>();

// Group sections by category
const groupedSections = computed(() => {
  const groups: Record<string, ConfigSection[]> = {};
  for (const section of props.sections) {
    if (!groups[section.group]) {
      groups[section.group] = [];
    }
    groups[section.group].push(section);
  }
  return groups;
});

// Get current section index for prev/next navigation
const currentIndex = computed(() =>
  props.sections.findIndex(s => s.id === props.activeSection)
);

const canGoPrev = computed(() => currentIndex.value > 0);
const canGoNext = computed(() => currentIndex.value < props.sections.length - 1);

const currentSection = computed(() =>
  props.sections.find(s => s.id === props.activeSection)
);

function goToPrev() {
  if (canGoPrev.value) {
    emit('select', props.sections[currentIndex.value - 1].id);
  }
}

function goToNext() {
  if (canGoNext.value) {
    emit('select', props.sections[currentIndex.value + 1].id);
  }
}
</script>

<template>
  <div class="flex items-center gap-2">
    <!-- Prev Button -->
    <button
      class="p-2 rounded hover:bg-surface-hover disabled:opacity-50 disabled:cursor-not-allowed"
      :disabled="!canGoPrev"
      @click="goToPrev"
      title="Previous section"
    >
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
      </svg>
    </button>

    <!-- Section Dropdown -->
    <div class="relative group">
      <button
        class="flex items-center gap-2 px-3 py-2 rounded-lg bg-surface-tertiary hover:bg-surface-hover transition-colors min-w-[200px]"
      >
        <span class="text-lg">{{ currentSection?.icon }}</span>
        <span class="font-medium">{{ currentSection?.label }}</span>
        <svg class="w-4 h-4 ml-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      <!-- Dropdown Menu -->
      <div class="absolute top-full left-0 mt-1 w-64 bg-surface-secondary border border-border rounded-lg shadow-lg
                  opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-50">
        <div
          v-for="(groupSections, groupName) in groupedSections"
          :key="groupName"
          class="py-1"
        >
          <div class="px-3 py-1 text-xs font-semibold text-content-muted uppercase tracking-wider">
            {{ groupName }}
          </div>
          <button
            v-for="section in groupSections"
            :key="section.id"
            class="w-full flex items-center gap-2 px-3 py-2 text-left hover:bg-surface-hover transition-colors"
            :class="{ 'bg-surface-hover': section.id === activeSection }"
            @click="emit('select', section.id)"
          >
            <span class="text-lg">{{ section.icon }}</span>
            <span class="flex-1">{{ section.label }}</span>
            <span
              v-if="section.required"
              class="text-xs px-1.5 py-0.5 rounded bg-error/20 text-error"
            >
              Required
            </span>
            <span
              v-else
              class="text-xs px-1.5 py-0.5 rounded bg-surface-tertiary text-content-muted"
            >
              Optional
            </span>
          </button>
        </div>
      </div>
    </div>

    <!-- Next Button -->
    <button
      class="p-2 rounded hover:bg-surface-hover disabled:opacity-50 disabled:cursor-not-allowed"
      :disabled="!canGoNext"
      @click="goToNext"
      title="Next section"
    >
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
      </svg>
    </button>
  </div>
</template>
