<template>
  <section id="admission" class="py-20 bg-white">
    <div class="container mx-auto px-4">
      <div class="grid lg:grid-cols-3 gap-8">
        <!-- 왼쪽: 기존 입학안내 콘텐츠 -->
        <div class="lg:col-span-2">
          <div class="text-center mb-16">
            <h2 class="text-4xl mb-4">입학 안내</h2>
            <p class="text-lg text-gray-600">
              순천향대학교와 함께 꿈을 이루세요
            </p>
          </div>

          <div class="mb-16">
            <h3 class="text-2xl font-bold text-center mb-8">전형 일정</h3>
            <div class="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              <UiCard
                v-for="(step, index) in admissionSteps"
                :key="index"
                class="text-center hover:shadow-lg transition-shadow"
              >
                <CardHeader>
                  <div class="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-4 mx-auto">
                    <component :is="step.icon" class="w-8 h-8 text-blue-600" />
                  </div>
                  <CardTitle>{{ step.title }}</CardTitle>
                  <CardDescription>{{ step.description }}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div class="inline-block bg-blue-50 text-blue-700 px-4 py-2 rounded-full text-sm">
                    {{ step.date }}
                  </div>
                </CardContent>
              </UiCard>
            </div>
          </div>

          <div class="mb-16">
            <h3 class="text-2xl font-bold text-center mb-8">전형 유형</h3>
            <div class="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              <UiCard
                v-for="(type, index) in admissionTypes"
                :key="index"
                class="hover:shadow-lg transition-shadow"
              >
                <CardHeader>
                  <CardTitle class="text-center">{{ type.title }}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p class="text-gray-600 text-center mb-4">
                    {{ type.description }}
                  </p>
                  <div class="text-center">
                    <span class="inline-block bg-gray-100 px-4 py-2 rounded-full text-sm font-semibold">
                      모집인원: {{ type.quota }}
                    </span>
                  </div>
                </CardContent>
              </UiCard>
            </div>
          </div>

          <div class="bg-blue-50 rounded-lg p-8 text-center">
            <h3 class="text-2xl font-bold mb-4">입학 상담</h3>
            <p class="text-gray-700 mb-6">
              입학과 관련하여 궁금한 사항이 있으신가요?<br />
              전문 상담원이 친절하게 안내해드립니다.
            </p>
            <div class="flex flex-col sm:flex-row gap-4 justify-center">
              <UiButton size="lg" class="bg-blue-600 hover:bg-blue-700">
                <Phone class="w-5 h-5 mr-2" />
                전화 상담: 041-530-1000
              </UiButton>
              <UiButton size="lg" variant="outline">
                온라인 상담 신청
              </UiButton>
            </div>
          </div>
        </div>

        <!-- 오른쪽: 챗봇 박스 -->
        <div class="lg:col-span-1">
          <div class="sticky top-8">
            <UiCard class="hover:shadow-lg transition-shadow cursor-pointer" @click="$router.push('/chatbot')">
              <CardHeader class="text-center">
                <div class="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-4 mx-auto">
                  <MessageCircle class="w-8 h-8 text-blue-600" />
                </div>
                <CardTitle>챗봇 상담</CardTitle>
                <CardDescription>
                  AI 챗봇으로 빠르고 간편하게 입학 정보를 확인하세요
                </CardDescription>
              </CardHeader>
              <CardContent class="text-center">
                <UiButton class="w-full">
                  챗봇 시작하기
                </UiButton>
              </CardContent>
            </UiCard>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { Calendar, FileText, ClipboardCheck, Phone, MessageCircle } from 'lucide-vue-next'
import UiCard from '@/app/components/ui/Card.vue'
import CardContent from '@/app/components/ui/CardContent.vue'
import CardHeader from '@/app/components/ui/CardHeader.vue'
import CardTitle from '@/app/components/ui/CardTitle.vue'
import CardDescription from '@/app/components/ui/CardDescription.vue'
import UiButton from '@/app/components/ui/Button.vue'

const admissionSteps = [
  { icon: FileText, title: '원서 접수', description: '온라인 원서접수 시스템을 통해 지원', date: '2026년 9월' },
  { icon: ClipboardCheck, title: '서류 제출', description: '학생부 및 자기소개서 제출', date: '2026년 10월' },
  { icon: Calendar, title: '전형 일정', description: '면접 및 실기고사 실시', date: '2026년 11월' },
  { icon: Phone, title: '합격자 발표', description: '최종 합격자 발표 및 등록', date: '2026년 12월' },
]

const admissionTypes = [
  { title: '수시모집', description: '학생부종합전형, 학생부교과전형, 실기전형 등', quota: '약 70%' },
  { title: '정시모집', description: '수능 성적 기반 선발', quota: '약 30%' },
  { title: '편입학', description: '일반편입 및 학사편입', quota: '별도 선발' },
  { title: '특별전형', description: '농어촌학생, 기회균형선발 등', quota: '별도 선발' },
]
</script>
