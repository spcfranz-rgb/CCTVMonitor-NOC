<template>
  <div class="modal fade show d-block" style="background: rgba(0,0,0,0.8)" tabindex="-1">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content border-secondary bg-dark text-light">
        <div class="modal-header border-secondary">
          <h5 class="modal-title text-warning">Edit Hardware</h5>
          <button type="button" class="btn-close btn-close-white" @click="$emit('close')"></button>
        </div>
        
        <div class="modal-body bg-body-tertiary">
          <form @submit.prevent="submitForm">
            <div class="mb-3">
              <label class="form-label text-muted small fw-bold">Device Name (Unique)</label>
              <input type="text" class="form-control bg-dark text-light border-secondary" v-model="form.name" required>
            </div>
            
            <div class="mb-3">
              <label class="form-label text-muted small fw-bold">IP Address</label>
              <input type="text" class="form-control bg-dark text-light border-secondary font-monospace" v-model="form.ip" required>
            </div>

            <div v-if="type === 'cameras'" class="border-top border-secondary pt-3 mt-2">
              <div class="mb-3">
                <label class="form-label text-muted small fw-bold">RTSP Stream URL</label>
                <input type="text" class="form-control bg-dark text-light border-secondary font-monospace" v-model="form.stream_url" required>
              </div>

              <div class="row g-2 mb-3">
                <div class="col-6">
                  <label class="form-label text-muted small fw-bold">Uplink Switch</label>
                  <select class="form-select bg-dark text-light border-secondary" v-model="form.switch_id">
                    <option :value="null">Standalone</option>
                    <option v-for="sw in store.devices.switches" :key="sw.id" :value="sw.id">{{ sw.name }}</option>
                  </select>
                </div>
                <div class="col-6">
                  <label class="form-label text-muted small fw-bold">Manufacturer</label>
                  <select class="form-select bg-dark text-light border-secondary" v-model="form.manufacturer">
                    <option v-for="mfg in ['Other', 'Hikvision', 'Dahua', 'Amcrest', 'Axis', 'Foscam', 'Hanwha']" :key="mfg" :value="mfg">{{ mfg }}</option>
                  </select>
                </div>
              </div>

              <div class="row g-2">
                <div class="col-6">
                  <label class="form-label text-muted small fw-bold">Username</label>
                  <input type="text" class="form-control bg-dark text-light border-secondary" v-model="form.username">
                </div>
                <div class="col-6">
                  <label class="form-label text-muted small fw-bold">Password</label>
                  <input type="password" class="form-control bg-dark text-light border-secondary" v-model="form.password" placeholder="(Leave blank to keep)">
                </div>
              </div>
            </div>

            <button type="submit" class="btn btn-warning w-100 fw-bold mt-4" :disabled="saving">
              {{ saving ? 'Saving...' : 'Save Changes' }}
            </button>
          </form>

        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useSystemStore } from '../../stores/systemStore'

const props = defineProps(['device', 'type']) // type = 'switches', 'nvrs', or 'cameras'
const emit = defineEmits(['close'])
const store = useSystemStore()

const saving = ref(false)
const form = ref({})

onMounted(() => {
  // Clone the device data to avoid instantly mutating the grid behind the modal
  form.value = { ...props.device, password: '' }
})

const submitForm = async () => {
  saving.value = true
  try {
    const payload = { ...form.value }
    // Clean up empty password so it isn't submitted
    if (props.type === 'cameras' && !payload.password) {
      delete payload.password
    }

    await axios.put(`/api/v1/${props.type}/${props.device.id}`, payload)
    store.addToast(`Device updated successfully.`)
    await store.fetchSystemData() // Re-hydrate grids instantly
    emit('close')
  } catch (error) {
    store.addToast(error.response?.data?.message || 'Failed to update device.', 'danger')
  } finally {
    saving.value = false
  }
}
</script>
