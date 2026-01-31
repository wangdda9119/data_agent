<template>
  <section id="home" class="relative h-[600px] flex items-center justify-center overflow-hidden">
    <div class="absolute inset-0">
      <ImageWithFallback
        src="https://images.unsplash.com/photo-1664273891579-22f28332f3c4?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxtb2Rlcm4lMjB1bml2ZXJzaXR5JTIwY2FtcHVzJTIwYnVpbGRpbmd8ZW58MXx8fHwxNzY5ODMzODkwfDA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral"
        alt="순천향대학교 캠퍼스"
        class="w-full h-full object-cover"
      />
      <div class="absolute inset-0 bg-black/50" />
    </div>

    <div class="relative z-10 container mx-auto px-4 text-center text-white">
      <h1 class="text-5xl md:text-6xl mb-6 animate-fade-in">미래를 여는 대학</h1>
      <p class="text-xl md:text-2xl mb-8 max-w-2xl mx-auto">
        순천향대학교에서 여러분의 꿈을 실현하세요
      </p>
      <div class="flex flex-col sm:flex-row gap-4 justify-center">
        <UiButton size="lg" class="bg-blue-600 hover:bg-blue-700">입학 안내</UiButton>
        <UiButton
          size="lg"
          variant="outline"
          class="bg-white/10 text-white border-white hover:bg-white/20"
        >
          캠퍼스 둘러보기
        </UiButton>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import UiButton from '@/app/components/ui/Button.vue'
import ImageWithFallback from '@/app/components/figma/ImageWithFallback.vue'
</script>
