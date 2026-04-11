<template>
  <button
    type="button"
    :class="classes"
    @click="setActive"
  >
    <slot />
  </button>
</template>

<script setup lang="ts">
import { computed, inject } from 'vue'

type TabsCtx = {
  value: { get: () => string; set: (v: string) => void }
}

const props = defineProps<{ value: string }>()
const ctx = inject<TabsCtx>('tabs')

const isActive = computed(() => ctx?.value.get() === props.value)

const classes = computed(() => {
  const base =
    'inline-flex items-center justify-center whitespace-nowrap rounded-sm px-3 py-1.5 text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500'
  return isActive.value
    ? base + ' bg-white text-gray-900 shadow'
    : base + ' text-gray-600 hover:text-gray-900'
})

function setActive() {
  ctx?.value.set(props.value)
}
</script>
