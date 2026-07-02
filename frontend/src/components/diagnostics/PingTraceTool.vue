<!--
Copyright (c) 2026 Timothy Franz. All Rights Reserved.

This file is part of Project Lighthouse.
Unauthorized copying of this file, via any medium, is strictly prohibited.
Proprietary and confidential.
-->

<template>
  <div class="card shadow-sm border-secondary h-100">
    <div class="card-header bg-dark border-secondary">
      <h5 class="mb-0">ICMP / L3 Diagnostics</h5>
    </div>
    <div class="card-body bg-body-tertiary">
      <div class="input-group mb-3">
        <input type="text" class="form-control border-secondary bg-dark text-light" v-model="target" placeholder="192.168.1.1 or google.com">
        <button class="btn btn-outline-info fw-bold" @click="runDiagnostic('ping')" :disabled="loading">Ping</button>
        <button class="btn btn-outline-warning fw-bold" @click="runDiagnostic('trace')" :disabled="loading">Trace</button>
      </div>

      <div v-if="loading" class="text-center my-3 text-info">
        <div class="spinner-border spinner-border-sm" role="status"></div> Running diagnostic...
      </div>

      <pre v-if="output" class="bg-dark text-success p-3 rounded border border-secondary font-monospace" style="max-height: 300px; overflow-y: auto; white-space: pre-wrap; font-size: 0.85rem;">{{ output }}</pre>
    </div>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'
import axios from 'axios'
import { useSystemStore } from '../../stores/systemStore'

const store = useSystemStore()
const target = ref('')
const loading = ref(false)
const output = ref('')

const runDiagnostic = async (mode) => {
  if (!target.value) return;
  loading.value = true;
  output.value = '';

  try {
    if (mode === 'ping') {
      // Ping blocks eventlet briefly, returns standard JSON
      const res = await axios.post('/api/ping', { ip: target.value });
      output.value = res.data.output;
      loading.value = false;
    } else {
      // Traceroute is slow. Backend dispatches an eventlet thread and streams via Socket.IO
      store.listen('traceroute_result', (data) => {
        if (data.success) output.value = data.output;
        else output.value = "Error: " + data.error;
        loading.value = false;
        store.unlisten('traceroute_result');
      });
      await axios.post('/api/traceroute', { target: target.value, sid: store.socketId });
    }
  } catch (error) {
    output.value = "Diagnostic request failed.";
    loading.value = false;
  }
}

onUnmounted(() => {
  store.unlisten('traceroute_result')
})
</script>
