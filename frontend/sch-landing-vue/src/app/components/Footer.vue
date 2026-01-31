<template>
  <footer class="bg-gray-900 text-gray-300">
    <div class="container mx-auto px-4 py-12">
      <div class="grid md:grid-cols-2 lg:grid-cols-6 gap-8 mb-8">
        <div class="lg:col-span-2">
          <div class="flex items-center mb-4">
            <div class="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center">
              <span class="text-white font-bold text-lg">SCH</span>
            </div>
            <span class="ml-3 font-bold text-xl text-white">순천향대학교</span>
          </div>
          <p class="text-sm mb-4">
            인간 사랑과 생명 존중의 정신으로<br />
            미래를 선도하는 글로벌 인재를 양성합니다.
          </p>
          <div class="flex gap-4">
            <a href="#" class="hover:text-white transition-colors" aria-label="Facebook">
              <Facebook class="w-5 h-5" />
            </a>
            <a href="#" class="hover:text-white transition-colors" aria-label="Instagram">
              <Instagram class="w-5 h-5" />
            </a>
            <a href="#" class="hover:text-white transition-colors" aria-label="YouTube">
              <Youtube class="w-5 h-5" />
            </a>
          </div>
        </div>

        <div v-for="(section, index) in footerLinks" :key="index">
          <h3 class="text-white font-bold mb-4">{{ section.title }}</h3>
          <ul class="space-y-2">
            <li v-for="(link, linkIndex) in section.links" :key="linkIndex">
              <a href="#" class="text-sm hover:text-white transition-colors">
                {{ link }}
              </a>
            </li>
          </ul>
        </div>
      </div>

      <div class="border-t border-gray-800 pt-8">
        <div class="grid md:grid-cols-3 gap-4 mb-6">
          <div class="flex items-start gap-2">
            <MapPin class="w-5 h-5 mt-1 flex-shrink-0" />
            <div class="text-sm">
              <p class="font-semibold text-white mb-1">아산캠퍼스</p>
              <p>충청남도 아산시 신창면 순천향로 22</p>
            </div>
          </div>
          <div class="flex items-start gap-2">
            <Phone class="w-5 h-5 mt-1 flex-shrink-0" />
            <div class="text-sm">
              <p class="font-semibold text-white mb-1">대표전화</p>
              <p>041-530-1114</p>
            </div>
          </div>
          <div class="flex items-start gap-2">
            <Mail class="w-5 h-5 mt-1 flex-shrink-0" />
            <div class="text-sm">
              <p class="font-semibold text-white mb-1">이메일</p>
              <p>webmaster@sch.ac.kr</p>
            </div>
          </div>
        </div>

        <div class="text-sm text-center md:text-left">
          <p>&copy; 2026 순천향대학교. All rights reserved.</p>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { Mail, Phone, MapPin, Facebook, Instagram, Youtube } from 'lucide-vue-next'

const footerLinks = [
  { title: '대학안내', links: ['총장 인사말', '대학 연혁', '조직도', '캠퍼스맵'] },
  { title: '입학안내', links: ['모집요강', '전형일정', '학과안내', '입학상담'] },
  { title: '학사정보', links: ['학사일정', '수강신청', '장학금', '증명서발급'] },
  { title: '커뮤니티', links: ['공지사항', '뉴스', '이벤트', '취업정보'] },
]
</script>
