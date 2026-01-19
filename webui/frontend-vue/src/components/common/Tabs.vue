<script setup lang="ts">
import { computed, ref } from 'vue';

interface Tab {
  id: string;
  label: string;
  icon?: string;
  badge?: string | number;
  disabled?: boolean;
}

interface Props {
  tabs: Tab[];
  modelValue: string;
  variant?: 'underline' | 'pills' | 'boxed';
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'underline',
});

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void;
}>();

const tabRefs = ref<HTMLButtonElement[]>([]);

const activeTab = computed({
  get: () => props.modelValue,
  set: (value: string) => emit('update:modelValue', value),
});

const activeTabIndex = computed(() => {
  return props.tabs.findIndex((tab) => tab.id === activeTab.value);
});

const selectTab = (tab: Tab) => {
  if (!tab.disabled) {
    activeTab.value = tab.id;
  }
};

const handleKeydown = (event: KeyboardEvent, index: number) => {
  const enabledTabs = props.tabs.filter((tab) => !tab.disabled);
  const currentEnabledIndex = enabledTabs.findIndex((tab) => tab.id === props.tabs[index].id);

  let newIndex = -1;

  switch (event.key) {
    case 'ArrowLeft':
    case 'ArrowUp':
      event.preventDefault();
      // Find previous enabled tab
      newIndex = currentEnabledIndex - 1;
      if (newIndex < 0) newIndex = enabledTabs.length - 1;
      break;
    case 'ArrowRight':
    case 'ArrowDown':
      event.preventDefault();
      // Find next enabled tab
      newIndex = currentEnabledIndex + 1;
      if (newIndex >= enabledTabs.length) newIndex = 0;
      break;
    case 'Home':
      event.preventDefault();
      newIndex = 0;
      break;
    case 'End':
      event.preventDefault();
      newIndex = enabledTabs.length - 1;
      break;
    default:
      return;
  }

  if (newIndex >= 0 && newIndex < enabledTabs.length) {
    const targetTab = enabledTabs[newIndex];
    const targetIndex = props.tabs.findIndex((tab) => tab.id === targetTab.id);
    selectTab(targetTab);
    // Focus the new tab button
    tabRefs.value[targetIndex]?.focus();
  }
};

const baseTabClasses = 'flex items-center gap-2 font-medium transition-colors';

const variantClasses = {
  underline: {
    container: 'flex border-b border-border',
    tab: `${baseTabClasses} px-4 py-2 -mb-px border-b-2 border-transparent hover:text-content hover:border-border`,
    active: 'text-kometa-gold border-kometa-gold',
    inactive: 'text-content-secondary',
  },
  pills: {
    container: 'flex gap-1 p-1 bg-surface-tertiary rounded-lg',
    tab: `${baseTabClasses} px-3 py-1.5 rounded-md hover:text-content`,
    active: 'bg-surface-primary text-content shadow-sm',
    inactive: 'text-content-secondary',
  },
  boxed: {
    container: 'flex gap-2',
    tab: `${baseTabClasses} px-4 py-2 border border-border rounded-md hover:border-kometa-gold`,
    active: 'bg-kometa-gold text-content-inverse border-kometa-gold',
    inactive: 'text-content-secondary bg-surface-secondary',
  },
};
</script>

<template>
  <div>
    <div
      :class="variantClasses[variant].container"
      role="tablist"
      aria-label="Tabs"
    >
      <button
        v-for="(tab, index) in tabs"
        :key="tab.id"
        :ref="(el) => { if (el) tabRefs[index] = el as HTMLButtonElement }"
        type="button"
        role="tab"
        :id="`tab-${tab.id}`"
        :aria-selected="tab.id === activeTab"
        :aria-controls="`tabpanel-${tab.id}`"
        :aria-disabled="tab.disabled"
        :tabindex="tab.id === activeTab ? 0 : -1"
        :class="[
          variantClasses[variant].tab,
          tab.id === activeTab
            ? variantClasses[variant].active
            : variantClasses[variant].inactive,
          { 'opacity-50 cursor-not-allowed': tab.disabled },
        ]"
        @click="selectTab(tab)"
        @keydown="handleKeydown($event, index)"
      >
        <span
          v-if="tab.icon"
          class="text-lg"
          aria-hidden="true"
          v-html="tab.icon"
        />
        <span>{{ tab.label }}</span>
        <span
          v-if="tab.badge !== undefined"
          class="px-1.5 py-0.5 text-xs rounded-full bg-surface-tertiary"
          :aria-label="`${tab.badge} items`"
        >
          {{ tab.badge }}
        </span>
      </button>
    </div>

    <div
      :id="`tabpanel-${activeTab}`"
      role="tabpanel"
      :aria-labelledby="`tab-${activeTab}`"
      tabindex="0"
      class="mt-4"
    >
      <slot :active-tab="activeTab" />
    </div>
  </div>
</template>
