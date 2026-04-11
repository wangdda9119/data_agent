import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/app/components/Home.vue'
import ChatbotPage from '@/app/components/ChatbotPage.vue'
import Mypage from '@/app/components/Mypage.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/chatbot',
    name: 'Chatbot',
    component: ChatbotPage
  },
  {
    path: '/mypage',
    name: 'Mypage',
    component: Mypage
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router