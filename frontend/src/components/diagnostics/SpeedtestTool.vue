<template>
  <div class="card shadow-sm border-secondary h-100">
    <div class="card-header bg-dark border-secondary d-flex justify-content-between align-items-center">
      <h5 class="mb-0">WAN Bandwidth (Ookla Native)</h5>
      
      <button v-if="canRun" class="btn btn-sm btn-outline-primary fw-bold" @click="runTest" :disabled="loading">Run Test</button>
    </div>
    
    <div class="card-body bg-body-tertiary">
      
      <div v-if="loading" class="text-center my-4">
        <div class="spinner-grow text-primary mb-3" role="status"></div>
        <div class="text-muted small fw-bold">Negotiating with nearest server... (May take 30s)</div>
      </div>

      <div v-if="error" class="alert alert-danger">{{ error }}</div>

      <div v-if="!loading && store.latestSpeedtest" class="row text-center g-3 mt-2">
        <div class="col-12 col-md-4">
          <div class="p-3 border border-secondary rounded bg-dark h-100">
            <div class="text-muted small fw-bold">PING</div>
            <div class="fs-4 fw-bold text-info">{{ formatNumber(store.latestSpeedtest.ping) }}<span class="fs-6 ms-1">ms</span></div>
          </div>
        </div>
        <div class="col-12 col-md-4">
          <div class="p-3 border border-secondary rounded bg-dark h-100">
            <div class="text-muted small fw-bold">DOWNLOAD</div>
            <div class="fs-4 fw-bold text-success">{{ formatNumber(store.latestSpeedtest.download) }}<span class="fs-6 ms-1">Mbps</span></div>
          </div>
        </div>
        <div class="col-12 col-md-4">
          <div class="p-3 border border-secondary rounded bg-dark h-100">
            <div class="text-muted small fw-bold">UPLOAD</div>
            <div class="fs-4 fw-bold text-warning">{{ formatNumber(store.latestSpeedtest.upload) }}<span class="fs-6 ms-1">Mbps</span></div>
          </div>
        </div>
        <div class="col-12 mt-3">
          <div class="small text-muted border-top border-secondary pt-2">
            <strong>ISP:</strong> {{ store.latestSpeedtest.isp }}<br>
            <strong>Target Server:</strong> {{ store.latestSpeedtest.server }}<br>
            <strong>Tested:</strong> {{ formatDate(store.latestSpeedtest.timestamp) }}
          </div>
        </div>
      </div>
      
      <div v-if="!loading && !store.latestSpeedtest && !error" class="text-center text-muted py-5">
        No recent speed tests on file.
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import axios from 'axios'
import { useSystemStore } from '../../stores/systemStore'

const store = useSystemStore()
const loading = ref(false)
const error = ref('')

const canRun = computed(() => {
  return ['admin', 'operator'].includes(store.user?.role)
})

const formatDate = (ts) => {
  return new Date(ts * 1000).toLocaleString()
}

// Ensure strict numeric extraction regardless of whether payload is "10.08" or "10.08 Mbps"
const formatNumber = (val) => {
  if (val === undefined || val === null) return '-';
  const num = parseFloat(String(val).replace(/[^\d.-]/g, ''));
  return isNaN(num) ? '-' : num;
}

const runTest = async () => {
  loading.value = true;
  error.value = '';

  // Local handler just to clear the spinning loader and catch errors for THIS manual request
  const tempHandler = (data) => {
    loading.value = false;
    if (!data.success) {
      error.value = data.error;
    }
    // Clean up ONLY this specific callback, leaving the global store listener perfectly intact
    store.unlisten('speedtest_result', tempHandler);
  };
  
  store.listen('speedtest_result', tempHandler);

  try {
    await axios.post('/api/speedtest', { sid: store.socketId });
  } catch (err) {
    error.value = "Failed to initiate test. Check permissions.";
    loading.value = false;
    store.unlisten('speedtest_result', tempHandler);
  }
}
</script>
