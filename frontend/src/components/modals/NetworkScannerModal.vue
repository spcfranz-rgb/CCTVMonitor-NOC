<template>
  <div class="modal fade show d-block" style="background: rgba(0,0,0,0.8)" tabindex="-1">
    <div class="modal-dialog modal-lg modal-dialog-centered modal-dialog-scrollable">
      <div class="modal-content border-secondary bg-dark text-light">
        <div class="modal-header border-secondary">
          <h5 class="modal-title text-success">🔍 Auto-Discover Cameras</h5>
          <button type="button" class="btn-close btn-close-white" @click="$emit('close')"></button>
        </div>
        <div class="modal-body bg-body-tertiary">
          
          <div class="d-flex gap-2 mb-4">
            <input type="text" class="form-control border-secondary bg-dark text-light font-monospace" v-model="subnet" placeholder="192.168.1.0/24">
            <button class="btn btn-success fw-bold text-nowrap" @click="runScan" :disabled="scanning">
              {{ scanning ? 'Scanning /24...' : 'Start Sweep' }}
            </button>
          </div>

          <div v-if="scanning" class="text-center my-5 text-success">
            <div class="spinner-border mb-3" role="status"></div>
            <div>Probing RTSP ports across {{ subnet }}...</div>
          </div>

          <div v-if="!scanning && scanComplete">
            <div v-if="discoveredIps.length === 0" class="alert alert-warning border-secondary">
              No new unmanaged cameras found on this subnet.
            </div>
            
            <div v-else>
              <h6 class="mb-3 text-muted border-bottom border-secondary pb-2">Select Cameras to Provision ({{ discoveredIps.length }} Found)</h6>
              <div class="row g-2 mb-4">
                <div class="col-md-4" v-for="ip in discoveredIps" :key="ip">
                  <div class="form-check bg-dark border border-secondary rounded p-2 ps-4">
                    <input class="form-check-input" type="checkbox" :value="ip" :id="`chk-${ip}`" v-model="selectedIps">
                    <label class="form-check-label font-monospace small" :for="`chk-${ip}`">{{ ip }}</label>
                  </div>
                </div>
              </div>

              <h6 class="mb-3 text-muted border-bottom border-secondary pb-2">Global Access Credentials</h6>
              <div class="row g-3">
                <div class="col-md-6">
                  <select class="form-select form-select-sm bg-dark text-light border-secondary" v-model="form.switch_id">
                    <option :value="null">-- Target Switch (Optional) --</option>
                    <option v-for="sw in store.devices.switches" :key="sw.id" :value="sw.id">{{ sw.name }} ({{ sw.ip }})</option>
                  </select>
                </div>
                <div class="col-md-6">
                  <select class="form-select form-select-sm bg-dark text-light border-secondary" v-model="form.manufacturer">
                    <option v-for="mfg in ['Other', 'Hikvision', 'Dahua', 'Amcrest', 'Axis', 'Foscam', 'Hanwha']" :key="mfg" :value="mfg">{{ mfg }}</option>
                  </select>
                </div>
                <div class="col-md-6">
                  <input type="text" class="form-control form-control-sm bg-dark text-light border-secondary" placeholder="ONVIF Username" v-model="form.username">
                </div>
                <div class="col-md-6">
                  <input type="password" class="form-control form-control-sm bg-dark text-light border-secondary" placeholder="ONVIF Password" v-model="form.password">
                </div>
              </div>
            </div>
          </div>

        </div>
        <div class="modal-footer border-secondary justify-content-between" v-if="!scanning && scanComplete && discoveredIps.length > 0">
          <span class="small text-muted">{{ selectedIps.length }} selected</span>
          <button type="button" class="btn btn-info fw-bold" @click="bulkAdd" :disabled="provisioning || selectedIps.length === 0">
            {{ provisioning ? 'Deep Probing & Adding...' : 'Bulk Provision Selected' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useSystemStore } from '../../stores/systemStore'

const emit = defineEmits(['close'])
const store = useSystemStore()

const subnet = ref('')
const scanning = ref(false)
const scanComplete = ref(false)
const provisioning = ref(false)
const discoveredIps = ref([])
const selectedIps = ref([])

const form = ref({ switch_id: null, manufacturer: 'Other', username: '', password: '' })

onMounted(() => {
  subnet.value = store.defaultSubnet
})

const runScan = async () => {
  if (!subnet.value) return;
  scanning.value = true;
  scanComplete.value = false;
  selectedIps.value = [];
  try {
    const res = await axios.post('/api/scan_network', { subnet: subnet.value });
    if (res.data.success) {
      discoveredIps.value = res.data.discovered;
      selectedIps.value = [...res.data.discovered]; // Select all by default
      scanComplete.value = true;
    } else {
      store.addToast(res.data.error || 'Scan failed', 'danger');
    }
  } catch (error) {
    store.addToast('Network scan request failed.', 'danger');
  } finally {
    scanning.value = false;
  }
}

const bulkAdd = async () => {
  provisioning.value = true;
  try {
    const payload = { ...form.value, ips: selectedIps.value }
    const res = await axios.post('/api/add_cameras_bulk', payload);
    if (res.data.success) {
      store.addToast(`Successfully provisioned ${res.data.added} cameras.`);
      await store.fetchSystemData(); // Refresh the grid instantly
      emit('close');
    } else {
      store.addToast(res.data.error || 'Bulk add failed', 'danger');
    }
  } catch (error) {
    store.addToast('Bulk provision request failed.', 'danger');
  } finally {
    provisioning.value = false;
  }
}
</script>
