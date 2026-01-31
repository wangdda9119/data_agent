<template>
  <button
    :type="type"
    :disabled="disabled"
    :class="classes"
    v-bind="$attrs"
  >
    <slot />
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'

type Variant = 'default' | 'outline'
type Size = 'sm' | 'md' | 'lg'

const props = withDefaults(defineProps<{
  variant?: Variant
  size?: Size
  type?: 'button' | 'submit' | 'reset'
  disabled?: boolean
}>(), {
  variant: 'default',
  size: 'md',
  type: 'button',
  disabled: false,
})

const base =
  'inline-flex items-center justify-center rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:pointer-events-none'

const variantClass = computed(() => {
  if (props.variant === 'outline') {
    return 'border border-gray-300 bg-transparent hover:bg-gray-50'
  }
  return 'bg-blue-600 text-white hover:bg-blue-700'
})

const sizeClass = computed(() => {
  if (props.size === 'sm') return 'h-9 px-3 text-sm'
  if (props.size === 'lg') return 'h-12 px-6 text-base'
  return 'h-10 px-4 text-sm'
})

const classes = computed(() => [base, variantClass.value, sizeClass.value].join(' '))
</script>
