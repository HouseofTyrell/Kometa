<script setup lang="ts">
import { watch, onMounted, onUnmounted, ref, nextTick } from 'vue';

interface Props {
  open: boolean;
  title?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
  closeOnOverlay?: boolean;
  closeOnEscape?: boolean;
  showCloseButton?: boolean;
  ariaDescribedby?: string;
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md',
  closeOnOverlay: true,
  closeOnEscape: true,
  showCloseButton: true,
});

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'update:open', value: boolean): void;
}>();

const modalRef = ref<HTMLDivElement | null>(null);
const previousActiveElement = ref<HTMLElement | null>(null);

const sizeClasses = {
  sm: 'max-w-sm',
  md: 'max-w-md',
  lg: 'max-w-lg',
  xl: 'max-w-xl',
  full: 'max-w-full mx-4',
};

const handleOverlayClick = () => {
  if (props.closeOnOverlay) {
    close();
  }
};

const getFocusableElements = (): HTMLElement[] => {
  if (!modalRef.value) return [];
  const focusableSelectors = [
    'button:not([disabled])',
    'input:not([disabled])',
    'select:not([disabled])',
    'textarea:not([disabled])',
    '[tabindex]:not([tabindex="-1"])',
    'a[href]',
  ].join(', ');
  return Array.from(modalRef.value.querySelectorAll<HTMLElement>(focusableSelectors));
};

const handleKeydown = (event: KeyboardEvent) => {
  if (!props.open) return;

  if (event.key === 'Escape' && props.closeOnEscape) {
    event.preventDefault();
    close();
    return;
  }

  // Focus trap - Tab key
  if (event.key === 'Tab') {
    const focusableElements = getFocusableElements();
    if (focusableElements.length === 0) return;

    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    if (event.shiftKey) {
      // Shift + Tab
      if (document.activeElement === firstElement) {
        event.preventDefault();
        lastElement.focus();
      }
    } else {
      // Tab
      if (document.activeElement === lastElement) {
        event.preventDefault();
        firstElement.focus();
      }
    }
  }
};

const close = () => {
  emit('close');
  emit('update:open', false);
};

// Lock body scroll and manage focus when modal is open
watch(
  () => props.open,
  async (isOpen) => {
    if (isOpen) {
      // Store the currently focused element to restore later
      previousActiveElement.value = document.activeElement as HTMLElement;
      document.body.style.overflow = 'hidden';

      // Focus the first focusable element after the modal opens
      await nextTick();
      const focusableElements = getFocusableElements();
      if (focusableElements.length > 0) {
        focusableElements[0].focus();
      } else if (modalRef.value) {
        modalRef.value.focus();
      }
    } else {
      document.body.style.overflow = '';
      // Restore focus to the previous element
      if (previousActiveElement.value) {
        previousActiveElement.value.focus();
      }
    }
  }
);

onMounted(() => {
  document.addEventListener('keydown', handleKeydown);
});

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown);
  document.body.style.overflow = '';
});
</script>

<template>
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="open"
        class="fixed inset-0 z-50 flex items-center justify-center"
      >
        <!-- Overlay -->
        <div
          class="absolute inset-0 bg-black/60 backdrop-blur-sm"
          @click="handleOverlayClick"
        />

        <!-- Modal content -->
        <div
          ref="modalRef"
          :class="[
            'relative w-full bg-surface-secondary border border-border rounded-lg shadow-xl',
            sizeClasses[size],
          ]"
          role="dialog"
          aria-modal="true"
          :aria-labelledby="title ? 'modal-title' : undefined"
          :aria-describedby="ariaDescribedby"
          tabindex="-1"
        >
          <!-- Header -->
          <div
            v-if="title || $slots.header || showCloseButton"
            class="flex items-center justify-between px-4 py-3 border-b border-border"
          >
            <slot name="header">
              <h2
                id="modal-title"
                class="text-lg font-semibold text-content-primary"
              >
                {{ title }}
              </h2>
            </slot>

            <button
              v-if="showCloseButton"
              type="button"
              class="p-1 rounded-md text-content-secondary hover:text-content hover:bg-surface-tertiary transition-colors"
              aria-label="Close modal"
              @click="close"
            >
              <svg
                class="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>

          <!-- Body -->
          <div class="p-4">
            <slot />
          </div>

          <!-- Footer -->
          <div
            v-if="$slots.footer"
            class="flex items-center justify-end gap-2 px-4 py-3 border-t border-border"
          >
            <slot name="footer" />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>
