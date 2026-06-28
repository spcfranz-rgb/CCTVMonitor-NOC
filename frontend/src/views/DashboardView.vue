<template>
  <div>
    <TopNav />
    
    <ul class="nav nav-tabs mb-4 border-secondary">
      <li class="nav-item">
        <a class="nav-link text-light" :class="{ 'active bg-dark border-secondary border-bottom-0 fw-bold': activeTab === 'monitoring' }" href="#" @click.prevent="activeTab = 'monitoring'">Monitoring</a>
      </li>
      <li class="nav-item">
        <a class="nav-link text-light" :class="{ 'active bg-dark border-secondary border-bottom-0 fw-bold': activeTab === 'diagnostics' }" href="#" @click.prevent="activeTab = 'diagnostics'">Diagnostics</a>
      </li>
      <li class="nav-item" v-if="store.user?.role === 'admin'">
        <a class="nav-link text-light" :class="{ 'active bg-dark border-secondary border-bottom-0 fw-bold': activeTab === 'admin' }" href="#" @click.prevent="activeTab = 'admin'">Administration</a>
      </li>
    </ul>

    <div v-if="activeTab === 'monitoring'">
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
    </div>

    <div v-if="activeTab === 'diagnostics'">
      <DiagnosticsTab />
    </div>

    <div v-if="activeTab === 'admin'">
      <AdminTab />
    </div>

    <WebRtcPreviewModal v-if="previewCam" :camera="previewCam" @close="previewCam = null" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import TopNav from '../components/layout/TopNav.vue'
import DeviceTable from '../components/monitoring/DeviceTable.vue'
import DiagnosticsTab from '../components/dashboard/DiagnosticsTab.vue'
import AdminTab from '../components/dashboard/AdminTab.vue'
import WebRtcPreviewModal from '../components/modals/WebRtcPreviewModal.vue'
import { useSystemStore } from '../stores/systemStore'

const store = useSystemStore()
const activeTab = ref('monitoring')
const previewCam = ref(null)

onMounted(() => {
  store.fetchSystemData()
})

const openPreview = (cam) => {
  previewCam.value = cam
}
</script>
