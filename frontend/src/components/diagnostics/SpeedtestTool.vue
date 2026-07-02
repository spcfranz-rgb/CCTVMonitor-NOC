<!--
Copyright (c) 2026 Timothy Franz. All Rights Reserved.

This file is part of Project Lighthouse.
Unauthorized copying of this file, via any medium, is strictly prohibited.
Proprietary and confidential.
-->

<template>
  <div class="card shadow-sm border-secondary h-100">
    <div class="card-header bg-dark border-secondary d-flex justify-content-between align-items-center">
      <h5 class="mb-0">WAN Bandwidth Diagnostics</h5>
      <div v-if="canRun" class="d-flex gap-2 align-items-center">
        <select v-model="selectedProvider" class="form-select form-select-sm bg-dark text-light border-secondary w-auto" @change="checkStatus" :disabled="loading || isInstalling">
          <option value="librespeed">LibreSpeed (Open Source)</option>
          <option value="ookla">Ookla (Proprietary)</option>
        </select>
        <button v-if="isReadyToRun" class="btn btn-sm btn-outline-primary fw-bold text-nowrap" @click="runTest" :disabled="loading">
          Run Test
        </button>
      </div>
    </div>
    
    <div class="card-body bg-body-tertiary">
      
      <div v-if="selectedProvider === 'ookla' && !ooklaInstalled && !loading && !isInstalling" class="alert alert-warning border-secondary mb-0 text-center py-4">
        <h5 class="alert-heading fw-bold">License Agreement Required</h5>
        <p class="small mb-4">
          The Ookla Speedtest CLI is proprietary software. By installing it, you agree to Ookla's 
          <a href="https://www.speedtest.net/about/eula" target="_blank" class="text-primary fw-bold">End User License Agreement</a> and 
          <a href="https://www.speedtest.net/about/privacy" target="_blank" class="text-primary fw-bold">Privacy Policy</a>.
        </p>
        <button class="btn btn-warning fw-bold px-4" @click="installOokla" :disabled="isInstalling">
          I Accept the EULA & Install Ookla CLI
        </button>
      </div>

      <div v-if="isInstalling" class="text-center my-5 text-warning">
        <div class="spinner-border mb-3" role="status"></div>
        <div class="text-muted small fw-bold">Downloading and provisioning proprietary binary...</div>
      </div>

      <div v-if="loading && !isInstalling" class="text-center my-5">
        <div class="spinner-grow text-primary mb-3" role="status"></div>
        <div class="text-muted small fw-bold">Negotiating with nearest server... (May take 30s)</div>
      </div>

      <div v-if="error" class="alert alert-danger">{{ error }}</div>

      <div v-if="!loading && !isInstalling && store.latestSpeedtest && isReadyToRun" class="row text-center g-3 mt-2">
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
            <span class="badge bg-secondary ms-2">{{ store.latestSpeedtest.provider || 'unknown' }}</span>
          </div>
        </div>
      </div>
      
      <div v-if="!loading && !isInstalling && !store.latestSpeedtest && !error && isReadyToRun" class="text-center text-muted py-5">
        No recent speed tests on file.
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { useSystemStore } from '../../stores/systemStore'

const store = useSystemStore()
const loading = ref(false)
const isInstalling = ref(false)
const error = ref('')

const selectedProvider = ref('librespeed')
const ooklaInstalled = ref(false)

const canRun = computed(() => {
  return ['admin', 'operator'].includes(store.user?.role)
})

const isReadyToRun = computed(() => {
  if (selectedProvider.value === 'librespeed') return true;
  return selectedProvider.value === 'ookla' && ooklaInstalled.value;
})

const formatDate = (ts) => {
  return new Date(ts * 1000).toLocaleString()
}

const formatNumber = (val) => {
  if (val === undefined || val === null) return '-';
  const num = parseFloat(String(val).replace(/[^\d.-]/g, ''));
  return isNaN(num) ? '-' : num;
}

const checkStatus = async () => {
  if (selectedProvider.value === 'ookla') {
    try {
      const res = await axios.get('/api/speedtest/status')
      ooklaInstalled.value = res.data.ookla_installed
    } catch (e) {
      error.value = "Failed to check provider status."
    }
  }
}

const installOokla = async () => {
  isInstalling.value = true;
  error.value = '';
  try {
    // Ensure your CSRF token is attached. Update 'store.csrfToken' 
    // to wherever you cache the token from /api/v1/auth/status
    await axios.post('/api/speedtest/install_ookla', {}, {
      headers: {
        'X-CSRFToken': store.csrfToken 
      }
    });
    
    ooklaInstalled.value = true;
    store.addToast("Ookla Speedtest CLI installed successfully.");
  } catch (e) {
    console.error("Installation Debug:", e.response?.data || e.message);
    
    if (e.response?.status === 400) {
      error.value = "Security Error: Missing CSRF Token in request headers.";
    } else {
      error.value = e.response?.data?.message || "Provisioning failed. Check browser console for details.";
    }
  } finally {
    isInstalling.value = false;
  }
};

const runTest = async () => {
  loading.value = true;
  error.value = '';

  const tempHandler = (data) => {
    loading.value = false;
    if (!data.success) {
      if (data.error === 'LICENSE_REQUIRED') {
        ooklaInstalled.value = false;
        error.value = ''; // Let the UI render the EULA gate
      } else {
        error.value = data.error;
      }
    }
    store.unlisten('speedtest_result', tempHandler);
  };
  
  store.listen('speedtest_result', tempHandler);

  try {
    await axios.post('/api/speedtest', { 
      sid: store.socketId,
      provider: selectedProvider.value 
    });
  } catch (err) {
    error.value = "Failed to initiate test. Check permissions.";
    loading.value = false;
    store.unlisten('speedtest_result', tempHandler);
  }
}

onMounted(() => {
  checkStatus()
})
</script>
