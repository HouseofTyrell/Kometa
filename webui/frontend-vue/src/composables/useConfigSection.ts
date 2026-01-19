import { computed } from 'vue';

/**
 * Composable for config section components that eliminates the repeated
 * updateField pattern across all 19+ config sections.
 *
 * Usage:
 * ```ts
 * const { config, updateField } = useConfigSection<PlexConfig>(props, emit);
 * ```
 */
export function useConfigSection<T extends Record<string, unknown>>(
  props: { modelValue: T },
  emit: (event: 'update:modelValue', value: T) => void
) {
  const config = computed({
    get: () => props.modelValue,
    set: (value) => emit('update:modelValue', value),
  });

  function updateField<K extends keyof T>(field: K, value: T[K]) {
    emit('update:modelValue', { ...props.modelValue, [field]: value });
  }

  /**
   * Update multiple fields at once
   */
  function updateFields(updates: Partial<T>) {
    emit('update:modelValue', { ...props.modelValue, ...updates });
  }

  /**
   * Reset a field to undefined (remove from config)
   */
  function resetField<K extends keyof T>(field: K) {
    const newConfig = { ...props.modelValue };
    delete newConfig[field];
    emit('update:modelValue', newConfig);
  }

  return {
    config,
    updateField,
    updateFields,
    resetField,
  };
}
