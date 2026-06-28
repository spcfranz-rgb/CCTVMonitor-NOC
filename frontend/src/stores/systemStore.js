import { defineStore } from 'pinia'
import { io } from 'socket.io-client'
import axios from 'axios'

export const useSystemStore = defineStore('system', {
  state: () => ({
    user: null,
    csrfToken: '',
    mqttOnline: false,
    uiOnline: false,
    logos: { company: null, customer: null },
    devices: { switches: [], nvrs: [], cameras: [] },
    toasts: []
  }),
  actions: {
    async checkAuth() {
      try {
        const { data } = await axios.get('/api/v1/system/init')
        this.user = { username: 'Admin', role: 'admin' } // Extracted from data.users ideally
        this.csrfToken = data.csrf_token || ''
        axios.defaults.headers.common['X-CSRFToken'] = this.csrfToken
        this.devices = { switches: data.switches, nvrs: data.nvrs, cameras: data.cameras }
        this.logos = data.logos
        this.initSocket()
        return true
      } catch (error) {
        this.user = null
        return false
      }
    },
    async logout() {
      await axios.post('/api/v1/auth/logout')
      this.user = null
      window.location.href = '/login'
    },
    addToast(message, type = 'success') {
      const id = Date.now()
      this.toasts.push({ id, message, type })
      setTimeout(() => { this.toasts = this.toasts.filter(t => t.id !== id) }, 4000)
    },
    initSocket() {
      const socket = io()
      socket.on('connect', () => { this.uiOnline = true })
      socket.on('disconnect', () => { this.uiOnline = false; this.mqttOnline = false })
      socket.on('gateway_status', (data) => { this.mqttOnline = data.mqtt })
      socket.on('state_change', (data) => {
        const target = this.devices[data.type]?.find(d => d.id === data.id)
        if (target) target.status = data.status
      })
    }
  }
})
