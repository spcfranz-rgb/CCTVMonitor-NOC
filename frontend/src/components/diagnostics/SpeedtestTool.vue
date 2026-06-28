<template>
  <div class="card shadow-sm border-secondary h-100">
    <div class="card-header bg-dark border-secondary d-flex justify-content-between align-items-center">
      <h5 class="mb-0">WAN Bandwidth (Ookla Native)</h5>
      <button class="btn btn-sm btn-outline-primary fw-bold" @click="runTest" :disabled="loading">Run Test</button>
    </div>
    
    <div class="card-body bg-body-tertiary">
      
      <div v-if="loading" class="text-center my-4">
        <div class="spinner-grow text-primary mb-3" role="status"></div>
        <div class="text-muted small fw-bold">Negotiating with nearest server... (May take 30s)</div>
      </div>

      <div v-if="error" class="alert alert-danger">{{ error }}</div>

      <div v-if="!loading && result" class="row text-center g-3 mt-2">
        <div class="col-4">
          <div class="p-3 border border-secondary rounded bg-dark">
            <div class="text-muted small fw-bold">PING</div>
            <div class="fs-4 fw-bold text-info">{{ result.ping }}<span class="fs-6 ms-1">ms</span></div>
          </div>
        </div>
        <div class="col-4">
          <div class="p-3 border border-secondary rounded bg-dark">
            <div class="text-muted small fw-bold">DOWNLOAD</div>
            <div class="fs-4 fw-bold text-success">{{ result.download }}</div>
          </div>
        </div>
        <div class="col-4">
          <div class="p-3 border border-secondary rounded bg-dark">
            <div class="text-muted small fw-bold">UPLOAD</div>
            <div class="fs-4 fw-bold text-warning">{{ result.upload }}</div>
          </div>
        </div>
        <div class="col-12 mt-3">
          <div class="small text-muted border-top border-secondary pt-2">
            <strong>ISP:</strong> {{ result.isp }}<br>
            <strong>Target Server:</strong> {{ result.server }}<br>
            <strong>Tested:</strong> {{ formatDate(result.timestamp) }}
          </div>
        </div>
      </div>
      
      <div v-if="!loading && !result && !error" class="text-center text-muted py-5">
        No recent speed tests on file.
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import { useSystemStore } from '../../stores/systemStore'

const store = useSystemStore()
const loading = ref(false)
const error = ref('')
const result = ref(null)

onMounted(() => {
  // Try parsing the latest result cached in SQLite from the boot payload
  if (store.latestSpeedtest) {
    result.value = store.latestSpeedtest
  }
})

const formatDate = (ts) => {
  return new Date(ts * 1000).toLocaleString()
}

const runTest = async () => {
  loading.value = true;
  error.value = '';
  result.value = null;

  store.listen('speedtest_result', (data) => {
    loading.value = false;
    if (data.success) {
      result.value = data;
    } else {
      error.value = data.error;
    }
    store.unlisten('speedtest_result');
  });

  try {
    await axios.post('/api/speedtest', { sid: store.socketId });
  } catch (err) {
    error.value = "Failed to initiate test.";
    loading.value = false;
  }
}

onUnmounted(() => {
  store.unlisten('speedtest_result')
})
</script>
