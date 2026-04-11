<template>
  <!-- 챗봇 버튼 -->
  <button
    v-if="!isOpen"
    @click="isOpen = true"
    class="fixed bottom-6 right-6 w-14 h-14 bg-blue-600 hover:bg-blue-700 text-white rounded-full shadow-lg flex items-center justify-center transition-all hover:scale-110 z-50"
    aria-label="챗봇 열기"
  >
    <MessageCircle class="w-6 h-6" />
  </button>

  <!-- 챗봇 창 -->
  <UiCard
    v-if="isOpen"
    class="fixed bottom-6 right-6 w-[380px] h-[600px] shadow-2xl flex flex-col z-50"
  >
    <!-- 헤더 -->
    <div class="bg-blue-600 text-white p-4 rounded-t-lg flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 bg-white rounded-full flex items-center justify-center">
          <span class="text-blue-600 font-bold">SCH</span>
        </div>
        <div>
          <div class="font-bold">순천향대 안내봇</div>
          <div class="text-xs text-blue-100">학교 정보를 안내해드립니다</div>
        </div>
      </div>
      <button
        @click="isOpen = false"
        class="hover:bg-blue-700 p-1 rounded transition-colors"
        aria-label="챗봇 닫기"
      >
        <X class="w-5 h-5" />
      </button>
    </div>

    <!-- 메시지 영역 -->
    <div class="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
      <div
        v-for="message in messages"
        :key="message.id"
        :class="['flex', message.isBot ? 'justify-start' : 'justify-end']"
      >
        <div
          :class="[
            'max-w-[80%] rounded-lg p-3',
            message.isBot ? 'bg-white text-gray-800 shadow' : 'bg-blue-600 text-white',
          ]"
        >
          <p class="text-sm whitespace-pre-wrap">{{ message.text }}</p>
          <p
            :class="[
              'text-xs mt-1',
              message.isBot ? 'text-gray-400' : 'text-blue-100',
            ]"
          >
            {{ formatTime(message.timestamp) }}
          </p>
        </div>
      </div>

      <!-- 빠른 질문 버튼 (처음에만 표시) -->
      <div v-if="messages.length === 1" class="space-y-2">
        <p class="text-xs text-gray-500 text-center">빠른 질문</p>
        <button
          v-for="(question, index) in quickQuestions"
          :key="index"
          @click="handleQuickQuestion(question)"
          class="w-full text-left text-sm p-2 bg-white hover:bg-blue-50 rounded-lg border border-gray-200 transition-colors"
        >
          {{ question }}
        </button>
      </div>

      <div ref="messagesEndRef" />
    </div>

    <!-- 입력 영역 -->
    <div class="p-4 border-t bg-white rounded-b-lg">
      <div class="flex gap-2">
        <input
          type="text"
          v-model="inputValue"
          @keydown.enter.prevent="handleSendMessage"
          placeholder="메시지를 입력하세요..."
          class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <UiButton
          @click="handleSendMessage"
          :disabled="!inputValue.trim()"
          class="bg-blue-600 hover:bg-blue-700"
        >
          <Send class="w-4 h-4" />
        </UiButton>
      </div>
    </div>
  </UiCard>
</template>

<script setup lang="ts">
import { nextTick, ref, watch } from 'vue'
import { MessageCircle, X, Send } from 'lucide-vue-next'
import UiButton from '@/app/components/ui/Button.vue'
import UiCard from '@/app/components/ui/Card.vue'
import { apiClient } from '@/api/client'

type Message = {
  id: string
  text: string
  isBot: boolean
  timestamp: Date
}

const isOpen = ref(false)
const messages = ref<Message[]>([
  {
    id: '1',
    text: '안녕하세요! 순천향대학교 안내 챗봇입니다. 궁금하신 점을 물어보세요.',
    isBot: true,
    timestamp: new Date(),
  },
])
const inputValue = ref('')
const messagesEndRef = ref<HTMLElement | null>(null)

function scrollToBottom() {
  messagesEndRef.value?.scrollIntoView({ behavior: 'smooth' })
}

watch(
  () => messages.value.length,
  async () => {
    await nextTick()
    scrollToBottom()
  }
)

async function handleSendMessage() {
  const text = inputValue.value.trim()
  if (!text) return

  const userMessage: Message = {
    id: Date.now().toString(),
    text,
    isBot: false,
    timestamp: new Date(),
  }

  messages.value = [...messages.value, userMessage]
  inputValue.value = ''

  try {
    const answer = await apiClient.chat(text)
    const botResponse: Message = {
      id: (Date.now() + 1).toString(),
      text: answer,
      isBot: true,
      timestamp: new Date(),
    }
    messages.value = [...messages.value, botResponse]
  } catch (error) {
    const errorMessage: Message = {
      id: (Date.now() + 1).toString(),
      text: '죄송합니다. 응답을 가져오는 중 오류가 발생했습니다.',
      isBot: true,
      timestamp: new Date(),
    }
    messages.value = [...messages.value, errorMessage]
  }
}

const quickQuestions = [
  '학교 위치가 어디인가요?',
  '입학 전형 일정이 궁금해요',
  '컴퓨터공학과에 대해 알려주세요',
  '기숙사 정보를 알고 싶어요',
]

function handleQuickQuestion(question: string) {
  inputValue.value = question
}

function formatTime(d: Date) {
  return d.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })
}
</script>
