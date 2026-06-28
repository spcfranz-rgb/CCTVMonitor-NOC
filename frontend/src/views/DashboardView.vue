<template>
  <div>
    <TopNav />
    
    <div class="row mb-4">
      <div class="col-lg-6 mb-4 mb-lg-0">
        <DeviceTable title="Network Switches" type="switches" :devices="store.devices.switches" />
      </div>
      <div class="col-lg-6">
        <DeviceTable title="Network Video Recorders" type="nvrs" :devices="store.devices.nvrs" />
      </div>
    </div>

    <div class="row">
      <div class="col-12">
        <DeviceTable title="Cameras" type="cameras" :devices="store.devices.cameras" @preview="openPreview" />
      </div>
    </div>

    <WebRtcPreviewModal v-if="previewCam" :camera="previewCam" @close="previewCam = null" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import TopNav from '../components/layout/TopNav.vue'
import DeviceTable from '../components/monitoring/DeviceTable.vue'
import WebRtcPreviewModal from '../components/modals/WebRtcPreviewModal.vue'
import { useSystemStore } from '../stores/systemStore'

const store = useSystemStore()
const previewCam = ref(null)

// Fetch the hardware grid once the dashboard loads
onMounted(() => {
  store.fetchSystemData()
})

const openPreview = (cam) => {
  previewCam.value = cam
}
</script>
