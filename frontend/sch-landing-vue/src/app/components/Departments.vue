<template>
  <section id="departments" class="py-20 bg-white">
    <div class="container mx-auto px-4">
      <div class="text-center mb-16">
        <h2 class="text-4xl mb-4">학과 정보</h2>
        <p class="text-lg text-gray-600">
          다양한 전공 분야에서 미래를 준비하세요
        </p>
      </div>

      <Tabs v-model="activeTab" :default-value="colleges[0]?.id" class="w-full">
        <TabsList class="grid w-full grid-cols-2 md:grid-cols-3 lg:grid-cols-6 mb-8">
          <TabsTrigger
            v-for="college in colleges"
            :key="college.id"
            :value="college.id"
            class="flex items-center gap-2"
          >
            <component :is="college.icon" class="w-4 h-4" />
            <span class="hidden sm:inline">{{ college.name }}</span>
          </TabsTrigger>
        </TabsList>

        <TabsContent
          v-for="college in colleges"
          :key="college.id"
          :value="college.id"
        >
          <div class="grid md:grid-cols-2 gap-6">
            <UiCard
              v-for="(dept, index) in college.departments"
              :key="index"
              class="hover:shadow-lg transition-shadow"
            >
              <CardHeader>
                <CardTitle>{{ dept.name }}</CardTitle>
                <CardDescription>{{ dept.description }}</CardDescription>
              </CardHeader>
              <CardContent>
                <button class="text-blue-600 hover:underline">
                  자세히 보기 →
                </button>
              </CardContent>
            </UiCard>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { GraduationCap, Code, Heart, Beaker, PenTool, Building2 } from 'lucide-vue-next'
import Tabs from '@/app/components/ui/Tabs.vue'
import TabsList from '@/app/components/ui/TabsList.vue'
import TabsTrigger from '@/app/components/ui/TabsTrigger.vue'
import TabsContent from '@/app/components/ui/TabsContent.vue'
import UiCard from '@/app/components/ui/Card.vue'
import CardHeader from '@/app/components/ui/CardHeader.vue'
import CardTitle from '@/app/components/ui/CardTitle.vue'
import CardDescription from '@/app/components/ui/CardDescription.vue'
import CardContent from '@/app/components/ui/CardContent.vue'

type College = {
  id: string
  name: string
  icon: any
  departments: { name: string; description: string }[]
}

const colleges: College[] = [
  {
    id: 'engineering',
    name: '공과대학',
    icon: Code,
    departments: [
      { name: '컴퓨터공학과', description: '소프트웨어 개발 및 인공지능 전문가 양성' },
      { name: '전자공학과', description: '반도체 및 전자회로 설계 전문가 양성' },
      { name: '건축학과', description: '창의적 건축 설계 및 친환경 건축 교육' },
      { name: '화학공학과', description: '신소재 및 에너지 기술 전문가 양성' },
    ],
  },
  {
    id: 'medicine',
    name: '의과대학',
    icon: Heart,
    departments: [
      { name: '의예과/의학과', description: '인간 중심 의료 전문가 양성' },
      { name: '간호학과', description: '전문 간호 인력 양성' },
      { name: '보건행정학과', description: '병원 경영 및 보건 정책 전문가 양성' },
      { name: '물리치료학과', description: '재활 치료 전문가 양성' },
    ],
  },
  {
    id: 'business',
    name: '경상대학',
    icon: Building2,
    departments: [
      { name: '경영학과', description: '글로벌 경영 리더 양성' },
      { name: '경제학과', description: '경제 분석 및 정책 전문가 양성' },
      { name: '회계학과', description: '회계 및 세무 전문가 양성' },
      { name: '국제통상학과', description: '무역 및 국제 비즈니스 전문가 양성' },
    ],
  },
  {
    id: 'humanities',
    name: '인문대학',
    icon: GraduationCap,
    departments: [
      { name: '한국어문학과', description: '국어 교육 및 한국 문화 전문가 양성' },
      { name: '영어영문학과', description: '글로벌 영어 커뮤니케이션 전문가 양성' },
      { name: '중국어학과', description: '중국어 및 중국 문화 전문가 양성' },
      { name: '사학과', description: '역사 연구 및 문화재 전문가 양성' },
    ],
  },
  {
    id: 'arts',
    name: '예술대학',
    icon: PenTool,
    departments: [
      { name: '시각디자인학과', description: '창의적 디자인 전문가 양성' },
      { name: '영상학과', description: '영화 및 영상 콘텐츠 제작 전문가 양성' },
      { name: '음악학과', description: '전문 음악가 및 음악 교육자 양성' },
      { name: '무용학과', description: '무용 예술 전문가 양성' },
    ],
  },
  {
    id: 'science',
    name: '자연과학대학',
    icon: Beaker,
    departments: [
      { name: '생명공학과', description: '바이오 기술 전문가 양성' },
      { name: '화학과', description: '화학 연구 및 응용 전문가 양성' },
      { name: '식품영양학과', description: '영양 및 식품 안전 전문가 양성' },
      { name: '환경보건학과', description: '환경 보호 및 보건 전문가 양성' },
    ],
  },
]

const activeTab = ref(colleges[0].id)
</script>
