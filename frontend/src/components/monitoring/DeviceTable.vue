<template>
  <div class="card h-100 shadow-sm border-secondary">
    <div class="card-header bg-dark border-secondary">
      <h5 class="mb-0">{{ title }}</h5>
    </div>
    <div class="card-body p-0">
      <div class="table-responsive">
        <table class="table table-sm table-hover align-middle text-nowrap mb-0">
          <thead>
            <tr>
              <th class="ps-3">Name</th>
              <th>IP/Host</th>
              <th v-if="type === 'cameras'">Switch</th>
              <th>Status</th>
              <th class="text-end pe-3">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="device in devices" :key="device.id">
              <td class="ps-3">
                {{ device.name }}
                <button v-if="type === 'cameras'" class="btn btn-sm btn-outline-secondary ms-2 py-0" @click="$emit('preview', device)">Preview</button>
              </td>
              <td>
                <div class="fw-bold">{{ device.ip }}</div>
                <div class="small text-muted font-monospace" style="font-size: 0.75rem;">{{ device.mac_address || 'Waiting for ARP...' }}</div>
              </td>
              <td v-if="type === 'cameras'"><small class="text-muted">{{ device.switch_name || 'Standalone' }}</small></td>
              <td>
                <span class="badge" :class="statusClass(device.status)">{{ device.status }}</span>
              </td>
              <td class="text-end pe-3">
                <a v-if="isPrivateLocation(device.ip)" :href="`/tunnel/${singularType}/${device.id}/`" target="_blank" class="badge bg-info text-decoration-none me-2">WebUI</a>
                
                <button class="btn btn-sm" :class="device.is_silenced ? 'btn-warning' : 'btn-outline-secondary'" @click="toggleSilence(device)" :disabled="working === device.id">
                  {{ device.is_silenced ? '🔇' : '🔔' }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import axios from 'axios'
import { useSystemStore } from '../../stores/systemStore'

const props = defineProps(['title', 'type', 'devices'])
const emit = defineEmits(['preview'])
const store = useSystemStore()
const working = ref(null)

const singularType = computed(() => {
  if (props.type === 'switches') return 'switch'
  if (props.type === 'nvrs') return 'nvr'
  if (props.type === 'cameras') return 'camera'
  return props.type
})

const statusClass = (status) => {
  if (status === 'UP') return 'bg-success'
  if (status?.includes('Silenced')) return 'bg-warning text-dark'
  if (status?.includes('DOWN') || status?.includes('UNREACHABLE') || status?.includes('ERR')) return 'bg-danger'
  return 'bg-secondary'
}

// SECURE UX: Validates RFC 1918 Private Subnets and Local mDNS
const isPrivateLocation = (ip) => {
  if (!ip) return false;
  
  // Always allow standard .local mDNS hostnames on the LAN
  if (ip.toLowerCase().endsWith('.local')) return true;

  const ipv4Regex = /^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$/;
  const match = ip.match(ipv4Regex);

  if (match) {
    const p1 = parseInt(match[1], 10);
    const p2 = parseInt(match[2], 10);

    // 10.0.0.0 - 10.255.255.255
    if (p1 === 10) return true;
    
    // 172.16.0.0 - 172.31.255.255
    if (p1 === 172 && p2 >= 16 && p2 <= 31) return true;
    
    // 192.168.0.0 - 192.168.255.255
    if (p1 === 192 && p2 === 168) return true;
  }

  // If it's a public IP or an external hostname (like google.com), hide the button.
  return false;
}

const toggleSilence = async (device) => {
  working.value = device.id
  const hours = device.is_silenced ? 0 : 24
  try {
    await axios.post('/api/v1/devices/silence', { type: singularType.value, id: device.id, hours })
    device.is_silenced = !device.is_silenced
    store.addToast(`Silence updated for ${device.name}`)
  } catch(e) {
    store.addToast('Failed to update silence', 'danger')
  } finally {
    working.value = null
  }
}
</script>
