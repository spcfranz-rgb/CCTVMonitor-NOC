<!--
Copyright (c) 2026 Timothy Franz. All Rights Reserved.

This file is part of Project Lighthouse.
Unauthorized copying of this file, via any medium, is strictly prohibited.
Proprietary and confidential.
-->

<template>
  <div class="modal fade show d-block" style="background: rgba(0,0,0,0.85)" tabindex="-1">
    <div class="modal-dialog modal-xl modal-dialog-centered modal-dialog-scrollable">
      <div class="modal-content border-secondary bg-dark text-light">
        <div class="modal-header border-secondary bg-dark">
          <h5 class="modal-title text-info">Merge Configuration</h5>
          <button type="button" class="btn-close btn-close-white" @click="$emit('close')"></button>
        </div>
        
        <div class="modal-body bg-body-tertiary">
          <div class="alert alert-info border-secondary py-2 small">
            <strong>Analysis Complete:</strong> 
            {{ analysis.clean_inserts.length }} new devices, 
            {{ analysis.conflicts.length }} naming/hardware conflicts found.
          </div>

          <div v-if="analysis.clean_inserts.length > 0" class="mb-4">
            <h6 class="text-success border-bottom border-secondary pb-2">Ready to Append ({{ analysis.clean_inserts.length }} Valid Devices)</h6>
            <div class="card bg-dark border-secondary">
              <div class="card-body p-0">
                <table class="table table-sm table-dark table-hover mb-0">
                  <thead>
                    <tr>
                      <th class="ps-3">Name</th>
                      <th>Type</th>
                      <th>IP Address</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(item, idx) in analysis.clean_inserts" :key="idx">
                      <td class="ps-3 fw-bold text-success">{{ item.data.name }}</td>
                      <td><span class="badge bg-secondary">{{ item.type.toUpperCase() }}</span></td>
                      <td class="font-monospace">{{ item.data.ip }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <div v-if="analysis.conflicts.length > 0">
            <h6 class="text-danger border-bottom border-secondary pb-2 mb-3">Resolve Conflicts</h6>
            
            <div v-for="(conflict, index) in analysis.conflicts" :key="index" class="card bg-dark border-danger mb-3">
              <div class="card-header border-danger py-2 d-flex justify-content-between align-items-center">
                <span class="fw-bold text-danger">⚠️ {{ conflict.reason }}</span>
                <span class="badge bg-secondary">{{ conflict.name }} ({{ conflict.type.toUpperCase() }})</span>
              </div>
              
              <div class="card-body p-0">
                <table class="table table-sm table-dark mb-0 align-middle">
                  <thead>
                    <tr>
                      <th class="ps-3 w-50">Current DB State</th>
                      <th class="w-50">Incoming CSV State (Editable)</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td class="ps-3 border-end border-secondary text-muted small">
                        <div>Name: {{ conflict.existing.name }}</div>
                        <div>IP: {{ conflict.existing.ip || 'N/A' }}</div>
                        <div>Type: {{ conflict.existing.manufacturer || 'N/A' }}</div>
                      </td>
                      <td>
                        <div v-if="conflict.resolution === 'overwrite'">
                          <input type="text" class="form-control form-control-sm bg-dark text-light border-secondary mb-1"
                                 v-model="conflict.incoming.name" placeholder="Name">
                          <input type="text" class="form-control form-control-sm bg-dark text-light border-secondary" 
                                 v-model="conflict.incoming.ip" placeholder="IP Address">
                        </div>
                        <div v-else class="text-warning small fw-bold">
                          <div>Name: {{ conflict.incoming.name }}</div>
                          <div>IP: {{ conflict.incoming.ip }}</div>
                          <div>Type: {{ conflict.incoming.manufacturer }}</div>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
              
              <div class="card-footer border-danger bg-dark py-2">
                <div class="btn-group w-100 shadow-sm">
                  <input type="radio" class="btn-check" :name="`res-${index}`" :id="`skip-${index}`" value="skip" v-model="conflict.resolution">
                  <label class="btn btn-outline-secondary fw-bold" :for="`skip-${index}`">Skip (Keep Existing)</label>

                  <input type="radio" class="btn-check" :name="`res-${index}`" :id="`overwrite-${index}`" value="overwrite" v-model="conflict.resolution">
                  <label class="btn btn-outline-danger fw-bold" :for="`overwrite-${index}`">Overwrite Target</label>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="modal-footer border-secondary justify-content-between bg-dark">
          <button type="button" class="btn btn-outline-secondary" @click="$emit('close')">Cancel</button>
          <button type="button" class="btn btn-info fw-bold px-4" @click="submitMerge" :disabled="processing">
            {{ processing ? 'Applying Changes...' : 'Execute Merge' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useSystemStore } from '../../stores/systemStore'

const props = defineProps(['analysis'])
const emit = defineEmits(['close', 'merged'])
const store = useSystemStore()
const processing = ref(false)

const submitMerge = async () => {
  processing.value = true
  try {
    const payload = {
      clean_inserts: props.analysis.clean_inserts,
      // Only send conflicts marked as 'overwrite'
      resolved_conflicts: props.analysis.conflicts
        .filter(c => c.resolution === 'overwrite')
        .map(c => ({
            type: c.type,
            data: c.incoming // Sends the edited 'incoming' data to the backend
        }))
    }
    
    const response = await axios.post('/api/v1/system/import/apply', payload)
    
    if (response.data.success) {
      store.addToast('Configuration successfully merged.')
      await store.fetchSystemData()
      emit('merged')
    } else {
      store.addToast(response.data.message || 'Merge failed.', 'danger')
    }
  } catch (error) {
    store.addToast('Failed to apply merge resolution.', 'danger')
  } finally {
    processing.value = false
  }
}
</script>
