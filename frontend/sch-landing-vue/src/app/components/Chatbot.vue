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

function getResponse(question: string): string {
  const q = question.toLowerCase()

  // 인사말
  if (q.includes('안녕') || q.includes('hi') || q.includes('hello')) {
    return '안녕하세요! 순천향대학교에 대해 무엇이 궁금하신가요?'
  }

  // 위치 관련
  if (q.includes('위치') || q.includes('어디') || q.includes('주소')) {
    return '순천향대학교는 충청남도 아산시 신창면 순천향로 22에 위치해 있습니다. 서울에서 KTX로 약 30분 거리로 접근성이 우수합니다.'
  }

  // 전화번호
  if (q.includes('전화') || q.includes('연락처')) {
    return '대표전화: 041-530-1114\n입학상담: 041-530-1000\n평일 오전 9시부터 오후 6시까지 상담 가능합니다.'
  }

  // 학과 관련
  if (q.includes('학과') || q.includes('전공') || q.includes('단과대')) {
    return '순천향대학교는 공과대학, 의과대학, 경상대학, 인문대학, 예술대학, 자연과학대학 등 6개 단과대학에 50개 이상의 학과가 있습니다. 구체적인 학과를 말씀해주시면 자세히 안내해드릴게요!'
  }

  // 컴퓨터공학과
  if (q.includes('컴퓨터') || q.includes('소프트웨어') || q.includes('코딩')) {
    return '컴퓨터공학과는 소프트웨어 개발 및 인공지능 전문가를 양성하는 학과입니다. 최신 프로그래밍 언어, AI, 빅데이터 등을 배우실 수 있습니다.'
  }

  // 의과대학
  if (q.includes('의대') || q.includes('의학') || q.includes('간호')) {
    return '의과대학은 의예과/의학과, 간호학과, 보건행정학과, 물리치료학과 등이 있으며, 인간 중심의 의료 전문가를 양성합니다.'
  }

  // 입학 관련
  if (q.includes('입학') || q.includes('모집') || q.includes('전형')) {
    return '2026년 입학 전형은 수시모집(약 70%)과 정시모집(약 30%)으로 나뉩니다.\n- 원서접수: 9월\n- 서류제출: 10월\n- 전형일정: 11월\n- 합격발표: 12월\n자세한 내용은 입학처(041-530-1000)로 문의해주세요.'
  }

  // 등록금
  if (q.includes('등록금') || q.includes('학비') || q.includes('장학금')) {
    return '등록금은 학과별로 상이하며, 다양한 장학금 제도를 운영하고 있습니다. 성적우수 장학금, 가계곤란 장학금, 국가장학금 등이 있습니다.'
  }

  // 기숙사
  if (q.includes('기숙사') || q.includes('생활관') || q.includes('숙소')) {
    return '교내 기숙사는 쾌적한 생활 환경을 제공하며, 신입생 우선 배정됩니다. 2인실, 4인실 등 다양한 형태가 있으며, 식사는 학생식당을 이용하실 수 있습니다.'
  }

  // 도서관
  if (q.includes('도서관') || q.includes('열람실')) {
    return '중앙도서관은 24시간 운영되는 최첨단 학습 공간입니다. 약 100만권의 장서와 전자자료를 보유하고 있으며, 개인 열람실과 그룹 스터디룸도 이용 가능합니다.'
  }

  // 취업률
  if (q.includes('취업') || q.includes('진로') || q.includes('취직')) {
    return '순천향대학교의 취업률은 약 85%로 높은 편입니다. 산학협력을 통한 현장실습, 취업박람회, 진로상담 등 다양한 취업 지원 프로그램을 운영하고 있습니다.'
  }

  // 교환학생
  if (q.includes('교환학생') || q.includes('해외') || q.includes('유학')) {
    return '200개 이상의 해외 대학과 교류 협정을 맺고 있으며, 교환학생 프로그램, 어학연수, 해외인턴십 등 다양한 글로벌 프로그램을 운영합니다.'
  }

  // 동아리
  if (q.includes('동아리') || q.includes('동호회') || q.includes('학회')) {
    return '학술, 문화예술, 체육, 봉사 등 다양한 분야의 100여개 동아리가 활동하고 있습니다. 학생회관에서 동아리 활동을 할 수 있습니다.'
  }

  // 식당
  if (q.includes('식당') || q.includes('밥') || q.includes('식사')) {
    return '교내에 학생식당, 교직원식당, 카페테리아 등이 있으며, 한식, 양식, 중식, 일식 등 다양한 메뉴를 합리적인 가격에 제공합니다.'
  }

  // 건학이념
  if (q.includes('이념') || q.includes('정신') || q.includes('가치')) {
    return '순천향대학교의 건학 이념은 "인간 사랑과 생명 존중"입니다. 창의적이고 실용적인 인재를 양성하여 사회에 기여하는 것을 목표로 합니다.'
  }

  // 캠퍼스
  if (q.includes('캠퍼스') || q.includes('시설')) {
    return '아름다운 자연환경 속에 최첨단 강의동, 실험실습동, 중앙도서관, 학생회관, 체육시설, 기숙사 등이 갖춰져 있습니다.'
  }

  // 기본 응답
  return [
    '해당 질문에 대한 답변을 찾지 못했습니다. 다음 키워드로 질문해보세요:',
    '',
    '• 위치/주소',
    '• 전화번호',
    '• 학과/전공',
    '• 입학/전형',
    '• 등록금/장학금',
    '• 기숙사',
    '• 도서관',
    '• 취업',
    '• 교환학생',
    '• 동아리',
    '',
    '또는 입학처(041-530-1000)로 문의해주세요.',
  ].join('\n')
}

function handleSendMessage() {
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

  setTimeout(() => {
    const botResponse: Message = {
      id: (Date.now() + 1).toString(),
      text: getResponse(text),
      isBot: true,
      timestamp: new Date(),
    }
    messages.value = [...messages.value, botResponse]
  }, 500)
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
