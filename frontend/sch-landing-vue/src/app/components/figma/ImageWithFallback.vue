<template>
  <img
    :src="currentSrc"
    :alt="alt"
    :class="class"
    @error="onError"
  />
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const props = withDefaults(defineProps<{
  src: string
  alt?: string
  class?: string
  fallbackSrc?: string
}>(), {
  alt: '',
  class: '',
  fallbackSrc: '',
})

const currentSrc = ref(props.src)

watch(
  () => props.src,
  (v) => {
    currentSrc.value = v
  }
)

function onError() {
  if (props.fallbackSrc && currentSrc.value !== props.fallbackSrc) {
    currentSrc.value = props.fallbackSrc
  }
}
</script>
