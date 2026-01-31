<template>
  <section id="about" class="py-20 bg-gray-50">
    <div class="container mx-auto px-4">
      <div class="text-center mb-16">
        <h2 class="text-4xl mb-4">순천향대학교 소개</h2>
        <p class="text-lg text-gray-600 max-w-2xl mx-auto">
          1978년 개교 이래 인재 양성과 지역 발전에 기여하며
          대한민국을 대표하는 명문 사립대학으로 성장해왔습니다.
        </p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
        <UiCard
          v-for="(stat, index) in stats"
          :key="index"
          class="text-center hover:shadow-lg transition-shadow"
        >
          <CardContent class="pt-6 pb-6">
            <div class="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-4">
              <component :is="stat.icon" class="w-8 h-8 text-blue-600" />
            </div>
            <div class="text-3xl font-bold mb-2">{{ stat.value }}</div>
            <div class="text-gray-600">{{ stat.label }}</div>
          </CardContent>
        </UiCard>
      </div>

      <div class="grid md:grid-cols-2 gap-8 items-center">
        <div>
          <h3 class="text-3xl mb-4">교육 비전</h3>
          <p class="text-gray-700 mb-4">
            순천향대학교는 '인간 사랑과 생명 존중'이라는 건학 이념을 바탕으로
            창의적이고 실용적인 인재를 양성합니다.
          </p>
          <ul class="space-y-3">
            <li class="flex items-start">
              <span class="inline-block w-2 h-2 bg-blue-600 rounded-full mt-2 mr-3" />
              <span>글로벌 경쟁력을 갖춘 인재 양성</span>
            </li>
            <li class="flex items-start">
              <span class="inline-block w-2 h-2 bg-blue-600 rounded-full mt-2 mr-3" />
              <span>산학협력 중심 실무 교육</span>
            </li>
            <li class="flex items-start">
              <span class="inline-block w-2 h-2 bg-blue-600 rounded-full mt-2 mr-3" />
              <span>학생 중심의 맞춤형 교육</span>
            </li>
            <li class="flex items-start">
              <span class="inline-block w-2 h-2 bg-blue-600 rounded-full mt-2 mr-3" />
              <span>최첨단 교육 인프라</span>
            </li>
          </ul>
        </div>

        <div class="relative h-[400px] rounded-lg overflow-hidden shadow-lg">
          <img
            src="https://images.unsplash.com/photo-1752920299180-e8fd9276c202?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzdHVkZW50cyUyMHN0dWR5aW5nJTIwbGlicmFyeXxlbnwxfHx8fDE3Njk3NDkyNDV8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral"
            alt="학생들 학습 모습"
            class="w-full h-full object-cover"
          />
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { BookOpen, Users, Award, Globe } from 'lucide-vue-next'
import UiCard from '@/app/components/ui/Card.vue'
import CardContent from '@/app/components/ui/CardContent.vue'

const stats = [
  { icon: BookOpen, label: '학과', value: '50+' },
  { icon: Users, label: '재학생', value: '12,000+' },
  { icon: Award, label: '취업률', value: '85%' },
  { icon: Globe, label: '국제교류', value: '200+' },
]
</script>
