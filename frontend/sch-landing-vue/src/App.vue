<template>
  <div class="min-h-screen bg-white">
    <Header />
    <main>
      <Hero />
      <About />
      <Departments />
      <Campus />
      <Admission />
    </main>
    <Footer />
    <Chatbot />
  </div>
</template>

<script setup lang="ts">
import Header from '@/app/components/Header.vue'
import Hero from '@/app/components/Hero.vue'
import About from '@/app/components/About.vue'
import Departments from '@/app/components/Departments.vue'
import Campus from '@/app/components/Campus.vue'
import Admission from '@/app/components/Admission.vue'
import Footer from '@/app/components/Footer.vue'
import Chatbot from '@/app/components/Chatbot.vue'
</script>
