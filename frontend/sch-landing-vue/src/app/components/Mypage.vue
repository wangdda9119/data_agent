<template>
  <div class="mypage-container">
    <div class="mypage-card">
      <h1>마이페이지</h1>
      <div v-if="loading" class="loading">로딩 중...</div>
      <div v-else-if="error" class="error">{{ error }}</div>
      <div v-else class="info-section">
        <div class="info-row">
          <span class="label">이메일</span>
          <span class="value">{{ userInfo.email }}</span>
        </div>
        <div class="info-row">
          <span class="label">닉네임</span>
          <span class="value">{{ userInfo.name }}</span>
        </div>
        <div class="info-row">
          <span class="label">수강 코스</span>
          <span class="value">{{ userInfo.course_name || '미등록' }}</span>
        </div>
      </div>
      <button @click="goHome" class="home-btn">홈으로</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const loading = ref(true)
const error = ref('')
const userInfo = ref({
  email: '',
  name: '',
  course_name: ''
})

onMounted(async () => {
  try {
    const token = localStorage.getItem('access_token')
    if (!token) {
      error.value = '로그인이 필요합니다'
      loading.value = false
      return
    }

    const response = await axios.get(`${import.meta.env.VITE_API_BASE_URL || ''}/api/mypage`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
    
    userInfo.value = response.data
    loading.value = false
  } catch (err: any) {
    error.value = err.response?.data?.detail || '데이터를 불러올 수 없습니다'
    loading.value = false
  }
})

const goHome = () => {
  router.push('/')
}
</script>

<style scoped>
.mypage-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #f5f5f5;
  padding: 20px;
}

.mypage-card {
  background: white;
  padding: 40px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  min-width: 400px;
}

h1 {
  margin-top: 0;
  color: #333;
  text-align: center;
}

.loading, .error {
  text-align: center;
  padding: 20px;
}

.error {
  color: red;
}

.info-section {
  margin: 30px 0;
}

.info-row {
  display: flex;
  justify-content: space-between;
  padding: 15px;
  margin: 10px 0;
  background: #f8f9fa;
  border-radius: 5px;
}

.label {
  font-weight: bold;
  color: #666;
}

.value {
  color: #333;
  font-size: 16px;
}

.home-btn {
  width: 100%;
  background: #6c757d;
  color: white;
  border: none;
  padding: 12px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 16px;
  margin-top: 20px;
}

.home-btn:hover {
  background: #5a6268;
}
</style>
