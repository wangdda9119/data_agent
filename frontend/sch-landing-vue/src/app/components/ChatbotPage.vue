<template>
  <div class="min-h-screen bg-gray-50">
    <Header />
    <main class="container mx-auto px-4 py-8">
      <div class="max-w-4xl mx-auto">
        <h1 class="text-3xl font-bold text-center mb-8">순천향대 안내봇</h1>
        <div class="bg-white rounded-lg shadow-lg p-6">
          <!-- 챗봇 인터페이스 -->
          <div class="flex flex-col h-[600px]">
            <!-- 헤더 -->
            <div class="bg-blue-600 text-white p-4 rounded-t-lg flex items-center gap-3 mb-4">
              <div class="w-10 h-10 bg-white rounded-full flex items-center justify-center">
                <span class="text-blue-600 font-bold">SCH</span>
              </div>
              <div>
                <div class="font-bold">순천향대 안내봇</div>
                <div class="text-xs text-blue-100">학교 정보를 안내해드립니다</div>
              </div>
            </div>

            <!-- 메시지 영역 -->
            <div class="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50 rounded-b-lg">
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
                </div>
              </div>
            </div>

            <!-- 입력 영역 -->
            <div class="mt-4 flex gap-2">
              <input
                v-model="inputMessage"
                @keypress.enter="sendMessage"
                placeholder="메시지를 입력하세요..."
                class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                @click="sendMessage"
                :disabled="!inputMessage.trim()"
                class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                전송
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>
    <Footer />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import Header from '@/app/components/Header.vue'
import Footer from '@/app/components/Footer.vue'

interface Message {
  id: number
  text: string
  isBot: boolean
}

const messages = ref<Message[]>([
  {
    id: 1,
    text: '안녕하세요! 순천향대학교 안내봇입니다. 무엇을 도와드릴까요?',
    isBot: true
  }
])

const inputMessage = ref('')
let messageId = 2

const sendMessage = async () => {
  if (!inputMessage.value.trim()) return

  // 사용자 메시지 추가
  messages.value.push({
    id: messageId++,
    text: inputMessage.value,
    isBot: false
  })

  const userMessage = inputMessage.value
  inputMessage.value = ''

  try {
    // 백엔드 API 호출
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || ''}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query: userMessage }),
    })

    if (response.ok) {
      const data = await response.json()
      messages.value.push({
        id: messageId++,
        text: data.answer,
        isBot: true
      })
    } else {
      throw new Error('API 요청 실패')
    }
  } catch (error) {
    console.error('챗봇 응답 오류:', error)
    messages.value.push({
      id: messageId++,
      text: '죄송합니다. 챗봇 서비스에 일시적인 문제가 발생했습니다. 잠시 후 다시 시도해주세요.',
      isBot: true
    })
  }
}
</script>