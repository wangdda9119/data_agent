import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/app/components/Home.vue'
import ChatbotPage from '@/app/components/ChatbotPage.vue'

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
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router