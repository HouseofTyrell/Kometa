<script setup lang="ts">
import { computed } from 'vue';

interface Props {
  content: string;
}

const props = defineProps<Props>();

// Simple YAML syntax highlighting
const highlightedLines = computed(() => {
  if (!props.content) return [];

  return props.content.split('\n').map((line) => {
    // Skip empty lines
    if (!line.trim()) {
      return { type: 'empty', content: line };
    }

    // Comments
    if (line.trim().startsWith('#')) {
      return { type: 'comment', content: line };
    }

    // Check for key-value pairs
    const keyMatch = line.match(/^(\s*)([^:\s][^:]*?)(:)(.*)$/);
    if (keyMatch) {
      const [, indent, key, colon, rest] = keyMatch;
      const trimmedRest = rest.trim();

      // Check if value is a string, number, boolean, null, or list item
      let valueType = 'string';
      if (trimmedRest === '' || trimmedRest.startsWith('#')) {
        valueType = 'none';
      } else if (trimmedRest === 'true' || trimmedRest === 'false') {
        valueType = 'boolean';
      } else if (trimmedRest === 'null' || trimmedRest === '~') {
        valueType = 'null';
      } else if (/^-?\d+(\.\d+)?$/.test(trimmedRest)) {
        valueType = 'number';
      } else if (trimmedRest.startsWith('"') || trimmedRest.startsWith("'")) {
        valueType = 'quoted-string';
      }

      return {
        type: 'key-value',
        indent,
        key,
        colon,
        value: rest,
        valueType,
      };
    }

    // List items
    const listMatch = line.match(/^(\s*)(-)(\s*)(.*)$/);
    if (listMatch) {
      const [, indent, dash, space, value] = listMatch;
      return {
        type: 'list-item',
        indent,
        dash,
        space,
        value,
      };
    }

    // Default - just text
    return { type: 'text', content: line };
  });
});
</script>

<template>
  <div class="yaml-highlight font-mono text-sm leading-relaxed">
    <div
      v-for="(line, index) in highlightedLines"
      :key="index"
      class="yaml-line"
    >
      <!-- Empty line -->
      <template v-if="line.type === 'empty'">
        <span>&nbsp;</span>
      </template>

      <!-- Comment -->
      <template v-else-if="line.type === 'comment'">
        <span class="text-content-muted italic">{{ line.content }}</span>
      </template>

      <!-- Key-value pair -->
      <template v-else-if="line.type === 'key-value'">
        <span class="text-content-muted">{{ line.indent }}</span>
        <span class="text-cyan-400 font-medium">{{ line.key }}</span>
        <span class="text-content-muted">{{ line.colon }}</span>
        <template v-if="line.valueType === 'none'">
          <span class="text-content-muted">{{ line.value }}</span>
        </template>
        <template v-else-if="line.valueType === 'boolean'">
          <span class="text-orange-400">{{ line.value }}</span>
        </template>
        <template v-else-if="line.valueType === 'null'">
          <span class="text-purple-400">{{ line.value }}</span>
        </template>
        <template v-else-if="line.valueType === 'number'">
          <span class="text-green-400">{{ line.value }}</span>
        </template>
        <template v-else-if="line.valueType === 'quoted-string'">
          <span class="text-amber-300">{{ line.value }}</span>
        </template>
        <template v-else>
          <span class="text-amber-300">{{ line.value }}</span>
        </template>
      </template>

      <!-- List item -->
      <template v-else-if="line.type === 'list-item'">
        <span class="text-content-muted">{{ line.indent }}</span>
        <span class="text-pink-400">{{ line.dash }}</span>
        <span>{{ line.space }}</span>
        <span class="text-amber-300">{{ line.value }}</span>
      </template>

      <!-- Default text -->
      <template v-else>
        <span>{{ line.content }}</span>
      </template>
    </div>
  </div>
</template>

<style scoped>
.yaml-highlight {
  counter-reset: line;
}

.yaml-line {
  min-height: 1.5em;
  white-space: pre;
}
</style>
