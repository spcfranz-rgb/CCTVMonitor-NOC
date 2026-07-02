<template>
  <div class="modal fade show d-block" style="background: rgba(0,0,0,0.8)" tabindex="-1">
    <div class="modal-dialog modal-lg modal-dialog-centered">
      <div class="modal-content border-secondary">
        <div class="modal-header bg-dark border-secondary">
          <h5 class="modal-title">Live Stream: {{ camera.name }}</h5>
          <button type="button" class="btn-close btn-close-white" @click="$emit('close')"></button>
        </div>
        <div class="modal-body text-center bg-dark p-0" style="min-height: 400px; position: relative;">
          
          <div v-if="loading" class="spinner-border text-primary position-absolute top-50 start-50 translate-middle"></div>
          
          <video v-show="!fallbackMode" ref="videoEl" class="w-100 h-100" autoplay muted playsinline controls style="background: black;"></video>
          
          <img v-if="fallbackMode" :src="snapshotUrl" class="w-100 h-100" style="object-fit: contain;">
        
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import { useSystemStore } from '../../stores/systemStore'

const props = defineProps(['camera'])
const emit = defineEmits(['close'])
const store = useSystemStore()

const videoEl = ref(null)
const loading = ref(true)
const fallbackMode = ref(false)
const snapshotUrl = ref('')

let peerConnection = null
let pollInterval = null

onMounted(async () => {
  try {
    // Inject the Context-Aware STUN/TURN servers pulled from the gateway
    const rtcConfig = store.webrtcConfig || { iceServers: [] };
    rtcConfig.iceTransportPolicy = "all"; // Allow both host (direct) and relay (TURN) candidates

    peerConnection = new RTCPeerConnection(rtcConfig)

    peerConnection.ontrack = (event) => {
      if (videoEl.value.srcObject !== event.streams[0]) {
        videoEl.value.srcObject = event.streams[0]
        loading.value = false
      }
    }

    peerConnection.addTransceiver('video', { direction: 'recvonly' })
    const offer = await peerConnection.createOffer()
    await peerConnection.setLocalDescription(offer)

    const response = await axios.post(`/api/webrtc/${props.camera.id}/whep`, offer.sdp, {
      headers: { 'Content-Type': 'application/sdp' }
    })

    await peerConnection.setRemoteDescription({ type: 'answer', sdp: response.data })

  } catch (error) {
    console.error("WebRTC Negotiation Failed:", error)
    initFallbackMode()
  }
})

const initFallbackMode = () => {
  loading.value = false
  fallbackMode.value = true
  store.addToast('WebRTC negotiation failed. Falling back to HTTP snapshot polling.', 'warning')
  
  const refresh = () => { snapshotUrl.value = `/api/snapshot/${props.camera.id}?t=${Date.now()}` }
  refresh()
  pollInterval = setInterval(refresh, 5000)
}

onUnmounted(() => {
  if (pollInterval) clearInterval(pollInterval)
  if (videoEl.value?.srcObject) {
    videoEl.value.srcObject.getTracks().forEach(t => t.stop())
    videoEl.value.srcObject = null
  }
  if (peerConnection) {
    peerConnection.close()
    peerConnection = null
  }
})
</script>
