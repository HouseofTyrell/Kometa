<script setup lang="ts">
import { computed } from 'vue';

interface Props {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  type?: 'button' | 'submit' | 'reset';
  fullWidth?: boolean;
  ariaLabel?: string;
  ariaDescribedby?: string;
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'md',
  disabled: false,
  loading: false,
  type: 'button',
  fullWidth: false,
});

const emit = defineEmits<{
  (e: 'click', event: MouseEvent): void;
}>();

const isDisabled = computed(() => props.disabled || props.loading);

const handleClick = (event: MouseEvent) => {
  if (!isDisabled.value) {
    emit('click', event);
  }
};

const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Enter' || event.key === ' ') {
    event.preventDefault();
    if (!isDisabled.value) {
      emit('click', event as unknown as MouseEvent);
    }
  }
};
</script>

<template>
  <button
    :type="type"
    :disabled="isDisabled"
    :aria-disabled="isDisabled"
    :aria-busy="loading"
    :aria-label="ariaLabel"
    :aria-describedby="ariaDescribedby"
    :class="[
      'btn',
      `btn-${size}`,
      `btn-${variant}`,
      { 'w-full': fullWidth, 'opacity-70 cursor-wait': loading },
    ]"
    @click="handleClick"
    @keydown="handleKeydown"
  >
    <span
      v-if="loading"
      class="spinner h-4 w-4"
      aria-hidden="true"
    />
    <span
      v-if="loading"
      class="sr-only"
    >Loading...</span>
    <slot v-if="!loading" />
  </button>
</template>
