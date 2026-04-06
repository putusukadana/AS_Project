<script setup>
import { ref } from 'vue'
import Login from './views/Login.vue'
import Register from './views/Register.vue'

const currentView = ref('login')

const toggleView = () => {
  currentView.value = currentView.value === 'login' ? 'register' : 'login'
}
</script>

<template>
  <div class="h-screen w-screen m-0 p-0 overflow-hidden font-sans">
    <Transition name="fade" mode="out-in">
      <Login v-if="currentView === 'login'" @toggleView="toggleView" />
      <Register v-else @toggleView="toggleView" />
    </Transition>
  </div>
</template>

<style>
/* Reset body styles set by default Vite template to ensure full screen coverage */
body {
  margin: 0 !important;
  display: block !important;
  min-width: 0 !important;
  min-height: 0 !important;
}
#app {
  width: 100%;
  height: 100%;
  margin: 0;
  padding: 0;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
