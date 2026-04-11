<template>
  <div :class="['rounded-lg border bg-white text-gray-900 shadow-sm', $attrs.class]" v-bind="restAttrs">
    <slot />
  </div>
</template>

<script setup lang="ts">
import { computed, useAttrs } from 'vue'

const attrs = useAttrs()
const restAttrs = computed(() => {
  const { class: _c, ...rest } = attrs
  return rest
})
</script>
