import { ref, computed, watch } from 'vue';

interface UndoRedoOptions {
  maxHistory?: number;
  debounceMs?: number;
}

export function useUndoRedo<T>(
  initialValue: T,
  options: UndoRedoOptions = {}
) {
  const { maxHistory = 50, debounceMs = 500 } = options;

  const current = ref<T>(initialValue) as ReturnType<typeof ref<T>>;
  const undoStack = ref<T[]>([]) as ReturnType<typeof ref<T[]>>;
  const redoStack = ref<T[]>([]) as ReturnType<typeof ref<T[]>>;

  let debounceTimer: ReturnType<typeof setTimeout> | null = null;
  let lastPushedValue: T | null = null;

  const canUndo = computed(() => undoStack.value.length > 0);
  const canRedo = computed(() => redoStack.value.length > 0);

  const historyLength = computed(() => undoStack.value.length);
  const futureLength = computed(() => redoStack.value.length);

  const pushToHistory = (value: T) => {
    // Don't push if value is the same as the last pushed value
    if (JSON.stringify(value) === JSON.stringify(lastPushedValue)) {
      return;
    }

    undoStack.value.push(JSON.parse(JSON.stringify(value)));
    lastPushedValue = JSON.parse(JSON.stringify(value));

    // Limit history size
    if (undoStack.value.length > maxHistory) {
      undoStack.value.shift();
    }

    // Clear redo stack when new changes are made
    redoStack.value = [];
  };

  const setValue = (value: T, addToHistory = true) => {
    if (debounceTimer) {
      clearTimeout(debounceTimer);
    }

    const previousValue = JSON.parse(JSON.stringify(current.value));
    current.value = value;

    if (addToHistory) {
      debounceTimer = setTimeout(() => {
        pushToHistory(previousValue);
      }, debounceMs);
    }
  };

  const setValueImmediate = (value: T) => {
    if (debounceTimer) {
      clearTimeout(debounceTimer);
    }

    const previousValue = JSON.parse(JSON.stringify(current.value));
    pushToHistory(previousValue);
    current.value = value;
  };

  const undo = () => {
    if (!canUndo.value) return;

    // Clear any pending debounce
    if (debounceTimer) {
      clearTimeout(debounceTimer);
      debounceTimer = null;
    }

    const previousValue = undoStack.value.pop();
    if (previousValue !== undefined) {
      redoStack.value.push(JSON.parse(JSON.stringify(current.value)));
      current.value = previousValue;
      lastPushedValue = previousValue;
    }
  };

  const redo = () => {
    if (!canRedo.value) return;

    // Clear any pending debounce
    if (debounceTimer) {
      clearTimeout(debounceTimer);
      debounceTimer = null;
    }

    const nextValue = redoStack.value.pop();
    if (nextValue !== undefined) {
      undoStack.value.push(JSON.parse(JSON.stringify(current.value)));
      current.value = nextValue;
      lastPushedValue = JSON.parse(JSON.stringify(current.value));
    }
  };

  const clearHistory = () => {
    undoStack.value = [];
    redoStack.value = [];
    lastPushedValue = null;
  };

  const reset = (value: T) => {
    clearHistory();
    current.value = value;
    lastPushedValue = null;
  };

  // Keyboard shortcuts
  const handleKeydown = (event: KeyboardEvent) => {
    const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
    const modifier = isMac ? event.metaKey : event.ctrlKey;

    if (modifier && event.key === 'z' && !event.shiftKey) {
      event.preventDefault();
      undo();
    } else if (
      (modifier && event.key === 'z' && event.shiftKey) ||
      (modifier && event.key === 'y')
    ) {
      event.preventDefault();
      redo();
    }
  };

  return {
    current,
    canUndo,
    canRedo,
    historyLength,
    futureLength,
    setValue,
    setValueImmediate,
    undo,
    redo,
    clearHistory,
    reset,
    handleKeydown,
  };
}
