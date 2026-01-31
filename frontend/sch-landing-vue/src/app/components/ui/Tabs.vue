<template>
  <div>
    <slot />
  </div>
</template>

<script setup lang="ts">
import { computed, provide, ref, watch } from 'vue'

type TabsCtx = {
  value: { get: () => string; set: (v: string) => void }
}

const props = defineProps<{
  modelValue?: string
  defaultValue?: string
}>()

const emit = defineEmits<{ (e: 'update:modelValue', v: string): void }>()

const inner = ref(props.modelValue ?? props.defaultValue ?? '')

watch(
  () => props.modelValue,
  (v) => {
    if (typeof v === 'string') inner.value = v
  }
)

const value = computed({
  get: () => inner.value,
  set: (v: string) => {
    inner.value = v
    emit('update:modelValue', v)
  },
})

provide<TabsCtx>('tabs', {
  value: {
    get: () => value.value,
    set: (v: string) => {
      value.value = v
    },
  },
})
</script>
