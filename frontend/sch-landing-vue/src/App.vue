<template>
  <div id="app">
    <router-view />
    <Chatbot />
  </div>
</template>

<script setup lang="ts">
import Chatbot from '@/app/components/Chatbot.vue'
</script>
