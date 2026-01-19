<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick, Teleport } from 'vue';

interface Option {
  value: string;
  label: string;
  description?: string;
  disabled?: boolean;
}

interface OptionGroup {
  label: string;
  icon?: string;
  description?: string;
  options: Option[];
}

interface Props {
  modelValue: string;
  groups: OptionGroup[];
  standaloneOptions?: Option[];
  placeholder?: string;
  disabled?: boolean;
  error?: string;
  label?: string;
  hint?: string;
  required?: boolean;
  id?: string;
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false,
  required: false,
  placeholder: 'Select an option...',
  standaloneOptions: () => [],
});

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void;
  (e: 'change', value: string): void;
}>();

const isOpen = ref(false);
const expandedGroups = ref<Set<string>>(new Set());
const dropdownRef = ref<HTMLElement | null>(null);
const buttonRef = ref<HTMLElement | null>(null);
const dropdownStyle = ref<Record<string, string>>({});

const selectId = computed(
  () => props.id || `expandable-select-${Math.random().toString(36).slice(2, 9)}`
);

// Find the selected option's label
const selectedLabel = computed(() => {
  if (!props.modelValue) return '';

  // Check standalone options first
  const standaloneOption = props.standaloneOptions?.find(o => o.value === props.modelValue);
  if (standaloneOption) return standaloneOption.label;

  // Check grouped options
  for (const group of props.groups) {
    const option = group.options.find(o => o.value === props.modelValue);
    if (option) return option.label;
  }

  return props.modelValue;
});

// Find the selected option's description
const selectedDescription = computed(() => {
  if (!props.modelValue) return '';

  const standaloneOption = props.standaloneOptions?.find(o => o.value === props.modelValue);
  if (standaloneOption) return standaloneOption.description || '';

  for (const group of props.groups) {
    const option = group.options.find(o => o.value === props.modelValue);
    if (option) return option.description || '';
  }

  return '';
});

function updateDropdownPosition() {
  if (!buttonRef.value) return;

  const rect = buttonRef.value.getBoundingClientRect();
  const viewportHeight = window.innerHeight;
  const spaceBelow = viewportHeight - rect.bottom;
  const spaceAbove = rect.top;
  const dropdownMaxHeight = 320; // max-h-80 = 20rem = 320px

  // Determine if dropdown should open upward or downward
  const openUpward = spaceBelow < dropdownMaxHeight && spaceAbove > spaceBelow;

  dropdownStyle.value = {
    position: 'fixed',
    left: `${rect.left}px`,
    width: `${rect.width}px`,
    maxHeight: `${Math.min(dropdownMaxHeight, openUpward ? spaceAbove - 8 : spaceBelow - 8)}px`,
    ...(openUpward
      ? { bottom: `${viewportHeight - rect.top + 4}px` }
      : { top: `${rect.bottom + 4}px` }
    ),
  };
}

function toggleDropdown() {
  if (props.disabled) return;
  isOpen.value = !isOpen.value;
}

function toggleGroup(groupLabel: string) {
  if (expandedGroups.value.has(groupLabel)) {
    expandedGroups.value.delete(groupLabel);
  } else {
    expandedGroups.value.add(groupLabel);
  }
}

function isGroupExpanded(groupLabel: string): boolean {
  return expandedGroups.value.has(groupLabel);
}

function selectOption(value: string) {
  emit('update:modelValue', value);
  emit('change', value);
  isOpen.value = false;
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
  <div class="w-full">
    <label
      v-if="label"
      :for="selectId"
      class="label"
    >
      {{ label }}
      <span
        v-if="required"
        class="text-error"
      >*</span>
    </label>

    <!-- Trigger Button -->
    <button
      ref="buttonRef"
      :id="selectId"
      type="button"
      :disabled="disabled"
      :class="[
        'input w-full text-left flex items-center justify-between cursor-pointer',
        { 'input-error': error },
        { 'opacity-50 cursor-not-allowed': disabled },
      ]"
      @click="toggleDropdown"
    >
      <span :class="modelValue ? 'text-content' : 'text-content-muted'">
        {{ selectedLabel || placeholder }}
      </span>
      <svg
        :class="['w-4 h-4 text-content-muted transition-transform', { 'rotate-180': isOpen }]"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M19 9l-7 7-7-7"
        />
      </svg>
    </button>

    <!-- Description below trigger -->
    <p v-if="selectedDescription && !isOpen" class="mt-1 text-sm text-content-secondary">
      {{ selectedDescription }}
    </p>

    <!-- Dropdown - Teleported to body to avoid overflow issues -->
    <Teleport to="body">
      <div
        v-if="isOpen"
        ref="dropdownRef"
        class="bg-surface-primary border border-border rounded-lg shadow-xl overflow-y-auto"
        :style="dropdownStyle"
        style="z-index: 9999;"
      >
        <!-- Standalone options at the top -->
        <div v-if="standaloneOptions && standaloneOptions.length > 0">
          <button
            v-for="option in standaloneOptions"
            :key="option.value"
            type="button"
            :disabled="option.disabled"
            :class="[
              'w-full px-4 py-2 text-left text-sm hover:bg-surface-secondary transition-colors',
              modelValue === option.value ? 'bg-kometa-gold/10 text-kometa-gold' : 'text-content',
              { 'opacity-50 cursor-not-allowed': option.disabled },
            ]"
            @click="selectOption(option.value)"
          >
            <div class="font-medium">{{ option.label }}</div>
            <div v-if="option.description" class="text-xs text-content-muted mt-0.5">
              {{ option.description }}
            </div>
          </button>
        </div>

        <!-- Divider if we have both standalone and groups -->
        <div v-if="standaloneOptions && standaloneOptions.length > 0 && groups.length > 0" class="border-t border-border my-1" />

        <!-- Option Groups -->
        <div v-for="group in groups" :key="group.label">
          <!-- Group Header (expandable) -->
          <button
            type="button"
            class="w-full px-4 py-2 flex items-center justify-between text-sm font-medium bg-surface-secondary hover:bg-surface-tertiary transition-colors"
            @click="toggleGroup(group.label)"
          >
            <div class="flex items-center gap-2">
              <span v-if="group.icon">{{ group.icon }}</span>
              <span>{{ group.label }}</span>
              <span class="text-xs text-content-muted">({{ group.options.length }})</span>
            </div>
            <svg
              :class="['w-4 h-4 text-content-muted transition-transform', { 'rotate-180': isGroupExpanded(group.label) }]"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M19 9l-7 7-7-7"
              />
            </svg>
          </button>

          <!-- Group Description -->
          <div v-if="group.description && isGroupExpanded(group.label)" class="px-4 py-1 text-xs text-content-muted bg-surface-secondary/50">
            {{ group.description }}
          </div>

          <!-- Group Options (shown when expanded) -->
          <div v-if="isGroupExpanded(group.label)" class="border-l-2 border-kometa-gold/30 ml-4">
            <button
              v-for="option in group.options"
              :key="option.value"
              type="button"
              :disabled="option.disabled"
              :class="[
                'w-full px-4 py-2 text-left text-sm hover:bg-surface-secondary transition-colors',
                modelValue === option.value ? 'bg-kometa-gold/10 text-kometa-gold' : 'text-content',
                { 'opacity-50 cursor-not-allowed': option.disabled },
              ]"
              @click="selectOption(option.value)"
            >
              <div class="font-medium">{{ option.label }}</div>
              <div v-if="option.description" class="text-xs text-content-muted mt-0.5">
                {{ option.description }}
              </div>
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <p
      v-if="error"
      class="mt-1 text-sm text-error"
    >
      {{ error }}
    </p>
    <p
      v-else-if="hint && !selectedDescription"
      class="mt-1 text-sm text-content-muted"
    >
      {{ hint }}
    </p>
  </div>
</template>
