<template>
  <section id="campus" class="py-20 bg-gray-50">
    <div class="container mx-auto px-4">
      <div class="text-center mb-16">
        <h2 class="text-4xl mb-4">캠퍼스 안내</h2>
        <p class="text-lg text-gray-600">
          최첨단 시설과 아름다운 자연이 조화를 이루는 캠퍼스
        </p>
      </div>

      <div class="mb-12 bg-white rounded-lg shadow-lg p-6">
        <div class="flex items-start gap-4 mb-4">
          <MapPin class="w-6 h-6 text-blue-600 mt-1" />
          <div>
            <h3 class="text-xl font-bold mb-2">캠퍼스 위치</h3>
            <p class="text-gray-700 mb-2">
              충청남도 아산시 신창면 순천향로 22
            </p>
            <p class="text-gray-600">
              서울에서 KTX로 30분, 수도권 접근성이 우수한 캠퍼스
            </p>
          </div>
        </div>
      </div>

      <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        <UiCard
          v-for="(facility, index) in facilities"
          :key="index"
          class="overflow-hidden hover:shadow-lg transition-shadow"
        >
          <div class="relative h-48">
            <img
              :src="facility.image"
              :alt="facility.title"
              class="w-full h-full object-cover"
            />
          </div>
          <CardContent class="pt-6">
            <div class="flex items-center gap-3 mb-2">
              <div class="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                <component :is="facility.icon" class="w-5 h-5 text-blue-600" />
              </div>
              <h3 class="text-xl font-bold">{{ facility.title }}</h3>
            </div>
            <p class="text-gray-600">{{ facility.description }}</p>
          </CardContent>
        </UiCard>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { MapPin, Building, Utensils, Library, Coffee, Home } from 'lucide-vue-next'
import UiCard from '@/app/components/ui/Card.vue'
import CardContent from '@/app/components/ui/CardContent.vue'

const facilities = [
  {
    icon: Library,
    title: '중앙도서관',
    description: '24시간 운영되는 최첨단 학습 공간',
    image:
      'https://images.unsplash.com/photo-1752920299180-e8fd9276c202?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzdHVkZW50cyUyMHN0dWR5aW5nJTIwbGlicmFyeXxlbnwxfHx8fDE3Njk3NDkyNDV8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral',
  },
  {
    icon: Building,
    title: '강의동',
    description: '스마트 강의실과 실습실 완비',
    image:
      'https://images.unsplash.com/photo-1757192420329-39acf20a12b8?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHx1bml2ZXJzaXR5JTIwY2xhc3Nyb29tJTIwbGVjdHVyZXxlbnwxfHx8fDE3Njk4MzM4OTF8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral',
  },
  {
    icon: Utensils,
    title: '학생식당',
    description: '다양한 메뉴를 제공하는 학생 식당',
    image:
      'https://images.unsplash.com/photo-1759092563843-6e17aa286dfe?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxjYW1wdXMlMjBncmVlbiUyMHNwYWNlfGVufDF8fHx8MTc2OTgzMzg5MXww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral',
  },
  {
    icon: Coffee,
    title: '학생회관',
    description: '휴식과 동아리 활동 공간',
    image:
      'https://images.unsplash.com/photo-1664273891579-22f28332f3c4?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxtb2Rlcm4lMjB1bml2ZXJzaXR5JTIwY2FtcHVzJTIwYnVpbGRpbmd8ZW58MXx8fHwxNzY5ODMzODkwfDA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral',
  },
  {
    icon: Home,
    title: '기숙사',
    description: '쾌적한 생활 환경을 제공하는 기숙사',
    image:
      'https://images.unsplash.com/photo-1759092563843-6e17aa286dfe?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxjYW1wdXMlMjBncmVlbiUyMHNwYWNlfGVufDF8fHx8MTc2OTgzMzg5MXww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral',
  },
  {
    icon: MapPin,
    title: '종합운동장',
    description: '체육 활동과 각종 행사 공간',
    image:
      'https://images.unsplash.com/photo-1759092563843-6e17aa286dfe?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxjYW1wdXMlMjBncmVlbiUyMHNwYWNlfGVufDF8fHx8MTc2OTgzMzg5MXww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral',
  },
]
</script>
