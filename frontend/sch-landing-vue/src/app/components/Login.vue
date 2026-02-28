<template>
  <div 
    class="fixed inset-0 z-[9999] flex items-center justify-center bg-black/50 p-4"
    @click.self="$emit('close')"
  >
    <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md">
      <div class="p-8">
        <h2 class="text-3xl font-bold text-gray-900 mb-8 text-center">로그인</h2>
        
        <form @submit.prevent="handleLogin" class="space-y-6">
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-2">이메일</label>
            <input
              v-model="email"
              type="email"
              required
              class="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none transition-colors"
              placeholder="example@email.com"
            />
          </div>
          
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-2">비밀번호</label>
            <input
              v-model="password"
              type="password"
              required
              class="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none transition-colors"
              placeholder="비밀번호를 입력하세요"
            />
          </div>
          
          <div v-if="error" class="bg-red-50 text-red-600 px-4 py-3 rounded-xl text-sm">
            {{ error }}
          </div>
          
          <button 
            type="submit" 
            class="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-xl transition-colors"
          >
            로그인
          </button>
          
          <div class="text-center space-y-2">
            <button
              type="button"
              @click="$emit('switch-to-signup')"
              class="text-sm text-blue-600 hover:text-blue-700 font-medium"
            >
              계정이 없으신가요? 회원가입
            </button>
            
            <div>
              <button
                type="button"
                @click="$emit('close')"
                class="text-sm text-gray-500 hover:text-gray-700"
              >
                닫기
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { apiClient } from '@/api/client'

const emit = defineEmits(['close', 'switch-to-signup', 'login-success'])

const email = ref('')
const password = ref('')
const error = ref('')

async function handleLogin() {
  error.value = ''
  try {
    await apiClient.login({ email: email.value, password: password.value })
    emit('login-success')
    emit('close')
  } catch (e) {
    error.value = '로그인에 실패했습니다. 이메일과 비밀번호를 확인해주세요.'
  }
}
</script>
