<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue';

export interface ConfigSection {
  id: string;
  label: string;
  icon: string;
  group: string;
  required?: boolean;
  children?: ConfigSection[];
}

interface Props {
  sections: ConfigSection[];
  activeSection: string;
}

const props = defineProps<Props>();
const emit = defineEmits<{
  (e: 'select', sectionId: string): void;
}>();

// Dropdown state - menu collapsed by default, but groups inside are expanded
const isOpen = ref(false);
const expandedGroups = ref<Set<string>>(new Set(['Core', 'Settings', 'Integrations', 'Metadata', 'Notifications'])); // All groups expanded by default
const expandedSections = ref<Set<string>>(new Set()); // For sections with children
const buttonRef = ref<HTMLElement | null>(null);
const dropdownRef = ref<HTMLElement | null>(null);
const dropdownStyle = ref<Record<string, string>>({});

// Flatten sections for navigation (includes children)
const flatSections = computed(() => {
  const flat: ConfigSection[] = [];
  for (const section of props.sections) {
    flat.push(section);
    if (section.children) {
      for (const child of section.children) {
        flat.push(child);
      }
    }
  }
  return flat;
});

// Group sections by category
const groupedSections = computed(() => {
  const groups: Record<string, ConfigSection[]> = {};
  // Define group order
  const groupOrder = ['Core', 'Settings', 'Integrations', 'Metadata', 'Notifications'];

  for (const section of props.sections) {
    if (!groups[section.group]) {
      groups[section.group] = [];
    }
    groups[section.group].push(section);
  }

  // Return in order
  const ordered: Record<string, ConfigSection[]> = {};
  for (const group of groupOrder) {
    if (groups[group]) {
      ordered[group] = groups[group];
    }
  }
  // Add any remaining groups
  for (const group of Object.keys(groups)) {
    if (!ordered[group]) {
      ordered[group] = groups[group];
    }
  }
  return ordered;
});

// Get current section index for prev/next navigation
const currentIndex = computed(() =>
  flatSections.value.findIndex(s => s.id === props.activeSection)
);

const canGoPrev = computed(() => currentIndex.value > 0);
const canGoNext = computed(() => currentIndex.value < flatSections.value.length - 1);

// Find the current section (might be a child)
const currentSection = computed(() => {
  // First check top-level sections
  const topLevel = props.sections.find(s => s.id === props.activeSection);
  if (topLevel) return topLevel;

  // Then check children
  for (const section of props.sections) {
    if (section.children) {
      const child = section.children.find(c => c.id === props.activeSection);
      if (child) return child;
    }
  }
  return null;
});

// Find parent section if current is a child
const parentSection = computed(() => {
  for (const section of props.sections) {
    if (section.children) {
      const child = section.children.find(c => c.id === props.activeSection);
      if (child) return section;
    }
  }
  return null;
});

function goToPrev() {
  if (canGoPrev.value) {
    emit('select', flatSections.value[currentIndex.value - 1].id);
  }
}

function goToNext() {
  if (canGoNext.value) {
    emit('select', flatSections.value[currentIndex.value + 1].id);
  }
}

function toggleDropdown() {
  isOpen.value = !isOpen.value;
}

function toggleGroup(groupName: string) {
  if (expandedGroups.value.has(groupName)) {
    expandedGroups.value.delete(groupName);
  } else {
    expandedGroups.value.add(groupName);
  }
}

function isGroupExpanded(groupName: string): boolean {
  return expandedGroups.value.has(groupName);
}

function toggleSection(sectionId: string) {
  if (expandedSections.value.has(sectionId)) {
    expandedSections.value.delete(sectionId);
  } else {
    expandedSections.value.add(sectionId);
  }
}

function isSectionExpanded(sectionId: string): boolean {
  return expandedSections.value.has(sectionId);
}

function selectSection(sectionId: string) {
  emit('select', sectionId);
  isOpen.value = false;
}

function handleSectionClick(section: ConfigSection, event: MouseEvent) {
  if (section.children && section.children.length > 0) {
    // If has children, toggle expansion instead of selecting
    event.stopPropagation();
    toggleSection(section.id);
  } else {
    // No children, select this section
    selectSection(section.id);
  }
}

function updateDropdownPosition() {
  if (!buttonRef.value) return;

  const rect = buttonRef.value.getBoundingClientRect();
  const viewportHeight = window.innerHeight;
  const spaceBelow = viewportHeight - rect.bottom;
  const dropdownMaxHeight = 450;

  // Determine if dropdown should open upward or downward
  const openUpward = spaceBelow < dropdownMaxHeight && rect.top > spaceBelow;

  dropdownStyle.value = {
    position: 'fixed',
    left: `${rect.left}px`,
    width: '300px',
    maxHeight: `${Math.min(dropdownMaxHeight, openUpward ? rect.top - 8 : spaceBelow - 8)}px`,
    ...(openUpward
      ? { bottom: `${viewportHeight - rect.top + 4}px` }
      : { top: `${rect.bottom + 4}px` }
    ),
  };
}

function handleClickOutside(event: MouseEvent) {
  const target = event.target as Node;
  if (
    dropdownRef.value &&
    !dropdownRef.value.contains(target) &&
    buttonRef.value &&
    !buttonRef.value.contains(target)
  ) {
    isOpen.value = false;
  }
}

function handleScroll() {
  if (isOpen.value) {
    updateDropdownPosition();
  }
}

function handleResize() {
  if (isOpen.value) {
    updateDropdownPosition();
  }
}

watch(isOpen, async (newVal) => {
  if (newVal) {
    await nextTick();
    updateDropdownPosition();
  }
});

onMounted(() => {
  document.addEventListener('click', handleClickOutside);
  window.addEventListener('scroll', handleScroll, true);
  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
  window.removeEventListener('scroll', handleScroll, true);
  window.removeEventListener('resize', handleResize);
});
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

    <!-- Section Dropdown Trigger -->
    <button
      ref="buttonRef"
      class="flex items-center gap-2 px-3 py-2 rounded-lg bg-surface-tertiary hover:bg-surface-hover transition-colors min-w-[200px]"
      @click="toggleDropdown"
    >
      <span class="text-lg">{{ currentSection?.icon }}</span>
      <div class="flex flex-col items-start">
        <span v-if="parentSection" class="text-xs text-content-muted">{{ parentSection.label }}</span>
        <span class="font-medium">{{ currentSection?.label }}</span>
      </div>
      <svg
        :class="['w-4 h-4 ml-auto transition-transform', { 'rotate-180': isOpen }]"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </button>

    <!-- Dropdown Menu - Teleported to body -->
    <Teleport to="body">
      <div
        v-if="isOpen"
        ref="dropdownRef"
        class="bg-surface-secondary border border-border rounded-lg shadow-xl overflow-y-auto"
        :style="dropdownStyle"
        style="z-index: 9999;"
      >
        <div
          v-for="(groupSections, groupName) in groupedSections"
          :key="groupName"
        >
          <!-- Group Header (expandable) -->
          <button
            type="button"
            class="w-full flex items-center justify-between px-3 py-2 text-left bg-surface-tertiary hover:bg-surface-hover transition-colors border-b border-border"
            @click="toggleGroup(String(groupName))"
          >
            <span class="text-xs font-semibold text-content-muted uppercase tracking-wider">
              {{ groupName }}
            </span>
            <div class="flex items-center gap-2">
              <span class="text-xs text-content-muted">({{ groupSections.length }})</span>
              <svg
                :class="['w-4 h-4 text-content-muted transition-transform', { 'rotate-180': isGroupExpanded(String(groupName)) }]"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </div>
          </button>

          <!-- Group Sections (shown when expanded) -->
          <div v-if="isGroupExpanded(String(groupName))" class="py-1">
            <div v-for="section in groupSections" :key="section.id">
              <!-- Section with children (expandable) -->
              <button
                v-if="section.children && section.children.length > 0"
                type="button"
                class="w-full flex items-center gap-2 px-3 py-2 text-left hover:bg-surface-hover transition-colors"
                :class="{ 'bg-kometa-gold/10': section.id === activeSection || section.children.some(c => c.id === activeSection) }"
                @click="handleSectionClick(section, $event)"
              >
                <span class="text-lg">{{ section.icon }}</span>
                <span
                  class="flex-1"
                  :class="{ 'text-kometa-gold font-medium': section.id === activeSection || section.children.some(c => c.id === activeSection) }"
                >
                  {{ section.label }}
                </span>
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
                <svg
                  :class="['w-4 h-4 text-content-muted transition-transform ml-1', { 'rotate-180': isSectionExpanded(section.id) }]"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              <!-- Children (shown when section is expanded) -->
              <div v-if="section.children && section.children.length > 0 && isSectionExpanded(section.id)" class="border-l-2 border-kometa-gold/30 ml-6 py-1">
                <button
                  v-for="child in section.children"
                  :key="child.id"
                  type="button"
                  class="w-full flex items-center gap-2 px-3 py-2 text-left hover:bg-surface-hover transition-colors"
                  :class="{ 'bg-kometa-gold/10': child.id === activeSection }"
                  @click="selectSection(child.id)"
                >
                  <span class="text-lg">{{ child.icon }}</span>
                  <span
                    class="flex-1"
                    :class="{ 'text-kometa-gold font-medium': child.id === activeSection }"
                  >
                    {{ child.label }}
                  </span>
                </button>
              </div>

              <!-- Section without children -->
              <button
                v-if="!section.children || section.children.length === 0"
                type="button"
                class="w-full flex items-center gap-2 px-3 py-2 text-left hover:bg-surface-hover transition-colors"
                :class="{ 'bg-kometa-gold/10': section.id === activeSection }"
                @click="selectSection(section.id)"
              >
                <span class="text-lg">{{ section.icon }}</span>
                <span
                  class="flex-1"
                  :class="{ 'text-kometa-gold font-medium': section.id === activeSection }"
                >
                  {{ section.label }}
                </span>
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
      </div>
    </Teleport>

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
