<template>
  <div v-if="isActive" class="mt-6">
    <slot />
  </div>
</template>

<script setup lang="ts">
import { computed, inject } from 'vue'

type TabsCtx = {
  value: { get: () => string; set: (v: string) => void }
}

const props = defineProps<{ value: string }>()
const ctx = inject<TabsCtx>('tabs')

const isActive = computed(() => ctx?.value.get() === props.value)
</script>
