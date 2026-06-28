<template>
  <div class="container py-4">
    <div aria-live="polite" aria-atomic="true" class="position-relative">
      <div class="toast-container position-fixed bottom-0 end-0 p-3" style="z-index: 1060;">
        <div v-for="toast in store.toasts" :key="toast.id" class="toast show align-items-center text-white border-0" :class="`bg-${toast.type}`" role="alert">
          <div class="d-flex">
            <div class="toast-body fw-bold">{{ toast.message }}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" @click="removeToast(toast.id)"></button>
          </div>
        </div>
      </div>
    </div>
    <router-view />
  </div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import { useSystemStore } from './stores/systemStore'
import { useRouter } from 'vue-router'

const store = useSystemStore()
const router = useRouter()

let idleTimer
const resetIdleTimer = () => {
  clearTimeout(idleTimer)
  idleTimer = setTimeout(() => {
    if (store.user) store.logout()
  }, 20 * 60 * 1000) // 20 mins
}

onMounted(() => {
  ['mousemove', 'keydown', 'scroll'].forEach(evt => window.addEventListener(evt, resetIdleTimer, { passive: true }))
  resetIdleTimer()
})

onUnmounted(() => {
  ['mousemove', 'keydown', 'scroll'].forEach(evt => window.removeEventListener(evt, resetIdleTimer))
})

const removeToast = (id) => {
  store.toasts = store.toasts.filter(t => t.id !== id)
}
</script>
