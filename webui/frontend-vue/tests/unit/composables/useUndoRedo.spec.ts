import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { useUndoRedo } from '@/composables/useUndoRedo';

describe('useUndoRedo', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('initializes with the initial value', () => {
    const { current } = useUndoRedo('initial');
    expect(current.value).toBe('initial');
  });

  it('can set a new value', () => {
    const { current, setValue } = useUndoRedo('initial');
    setValue('new value');
    expect(current.value).toBe('new value');
  });

  it('starts with empty undo/redo stacks', () => {
    const { canUndo, canRedo } = useUndoRedo('initial');
    expect(canUndo.value).toBe(false);
    expect(canRedo.value).toBe(false);
  });

  it('can undo after setting a value', () => {
    const { current, setValue, canUndo, undo } = useUndoRedo('initial');

    setValue('second');
    vi.advanceTimersByTime(600); // Wait for debounce

    expect(canUndo.value).toBe(true);

    undo();
    expect(current.value).toBe('initial');
  });

  it('can redo after undoing', () => {
    const { current, setValue, canRedo, undo, redo } = useUndoRedo('initial');

    setValue('second');
    vi.advanceTimersByTime(600);

    undo();
    expect(canRedo.value).toBe(true);

    redo();
    expect(current.value).toBe('second');
  });

  it('clears redo stack when new value is set', () => {
    const { current, setValue, canRedo, undo } = useUndoRedo('initial');

    setValue('second');
    vi.advanceTimersByTime(600);

    undo();
    expect(canRedo.value).toBe(true);

    setValue('third');
    vi.advanceTimersByTime(600);

    expect(canRedo.value).toBe(false);
  });

  it('setValueImmediate adds to history immediately', () => {
    const { current, setValueImmediate, canUndo, undo } = useUndoRedo('initial');

    setValueImmediate('second');

    expect(canUndo.value).toBe(true);

    undo();
    expect(current.value).toBe('initial');
  });

  it('respects maxHistory option', () => {
    const { setValueImmediate, historyLength } = useUndoRedo('initial', { maxHistory: 3 });

    setValueImmediate('value1');
    setValueImmediate('value2');
    setValueImmediate('value3');
    setValueImmediate('value4');

    expect(historyLength.value).toBe(3);
  });

  it('clearHistory removes all history', () => {
    const { setValueImmediate, canUndo, canRedo, clearHistory, undo } = useUndoRedo('initial');

    setValueImmediate('second');
    setValueImmediate('third');
    undo();

    expect(canUndo.value).toBe(true);
    expect(canRedo.value).toBe(true);

    clearHistory();

    expect(canUndo.value).toBe(false);
    expect(canRedo.value).toBe(false);
  });

  it('reset sets new value and clears history', () => {
    const { current, setValueImmediate, canUndo, reset } = useUndoRedo('initial');

    setValueImmediate('second');
    expect(canUndo.value).toBe(true);

    reset('reset value');

    expect(current.value).toBe('reset value');
    expect(canUndo.value).toBe(false);
  });

  it('works with objects', () => {
    const { current, setValueImmediate, undo } = useUndoRedo({ count: 0 });

    setValueImmediate({ count: 1 });
    setValueImmediate({ count: 2 });

    undo();
    expect(current.value).toEqual({ count: 1 });

    undo();
    expect(current.value).toEqual({ count: 0 });
  });

  it('does not add duplicate values to history', () => {
    const { setValueImmediate, historyLength } = useUndoRedo('initial');

    setValueImmediate('value1');
    setValueImmediate('value1'); // duplicate
    setValueImmediate('value1'); // duplicate

    expect(historyLength.value).toBe(1);
  });

  it('reports history and future lengths', () => {
    const { setValueImmediate, undo, historyLength, futureLength } = useUndoRedo('initial');

    setValueImmediate('value1');
    setValueImmediate('value2');

    expect(historyLength.value).toBe(2);
    expect(futureLength.value).toBe(0);

    undo();

    expect(historyLength.value).toBe(1);
    expect(futureLength.value).toBe(1);
  });

  it('handleKeydown responds to Ctrl+Z for undo', () => {
    const { setValueImmediate, handleKeydown, current } = useUndoRedo('initial');

    setValueImmediate('second');

    const event = {
      key: 'z',
      ctrlKey: true,
      shiftKey: false,
      metaKey: false,
      preventDefault: vi.fn(),
    } as unknown as KeyboardEvent;

    handleKeydown(event);

    expect(event.preventDefault).toHaveBeenCalled();
    expect(current.value).toBe('initial');
  });

  it('handleKeydown responds to Ctrl+Shift+Z for redo', () => {
    const { setValueImmediate, handleKeydown, undo, current } = useUndoRedo('initial');

    setValueImmediate('second');
    undo();

    const event = {
      key: 'z',
      ctrlKey: true,
      shiftKey: true,
      metaKey: false,
      preventDefault: vi.fn(),
    } as unknown as KeyboardEvent;

    handleKeydown(event);

    expect(event.preventDefault).toHaveBeenCalled();
    expect(current.value).toBe('second');
  });

  it('handleKeydown responds to Ctrl+Y for redo', () => {
    const { setValueImmediate, handleKeydown, undo, current } = useUndoRedo('initial');

    setValueImmediate('second');
    undo();

    const event = {
      key: 'y',
      ctrlKey: true,
      shiftKey: false,
      metaKey: false,
      preventDefault: vi.fn(),
    } as unknown as KeyboardEvent;

    handleKeydown(event);

    expect(event.preventDefault).toHaveBeenCalled();
    expect(current.value).toBe('second');
  });
});
