<template>
  <header class="sticky top-0 z-50 w-full border-b bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/60">
    <div class="container mx-auto flex h-16 items-center justify-between px-4">
      <div class="flex items-center gap-2">
        <div class="flex items-center">
          <div class="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center">
            <span class="text-white font-bold text-lg">SCH</span>
          </div>
          <span class="ml-3 font-bold text-xl">순천향대학교</span>
        </div>
      </div>

      <!-- Desktop Menu -->
      <nav class="hidden md:flex items-center gap-6">
        <a
          v-for="item in menuItems"
          :key="item.href"
          :href="item.href"
          class="text-sm hover:text-blue-600 transition-colors"
        >
          {{ item.label }}
        </a>
        <UiButton size="sm" class="ml-2">입학상담</UiButton>
      </nav>

      <!-- Mobile Menu Button -->
      <button
        class="md:hidden p-2"
        @click="isMenuOpen = !isMenuOpen"
        aria-label="Toggle menu"
      >
        <X v-if="isMenuOpen" :size="24" />
        <Menu v-else :size="24" />
      </button>
    </div>

    <!-- Mobile Menu -->
    <div v-if="isMenuOpen" class="md:hidden border-t bg-white">
      <nav class="flex flex-col py-4">
        <a
          v-for="item in menuItems"
          :key="item.href"
          :href="item.href"
          class="px-4 py-2 text-sm hover:bg-gray-50 hover:text-blue-600 transition-colors"
          @click="isMenuOpen = false"
        >
          {{ item.label }}
        </a>
        <div class="px-4 pt-2">
          <UiButton class="w-full">입학상담</UiButton>
        </div>
      </nav>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Menu, X } from 'lucide-vue-next'
import UiButton from '@/app/components/ui/Button.vue'

const isMenuOpen = ref(false)

const menuItems = [
  { label: '홈', href: '#home' },
  { label: '학교소개', href: '#about' },
  { label: '학과정보', href: '#departments' },
  { label: '캠퍼스', href: '#campus' },
  { label: '입학안내', href: '#admission' },
]
</script>
