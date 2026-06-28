import { defineStore } from 'pinia'
import { io } from 'socket.io-client'
import axios from 'axios'

export const useSystemStore = defineStore('system', {
  state: () => ({
    user: null,
    csrfToken: '',
    mqttOnline: false,
    uiOnline: false,
    devices: {
      switches: [],
      nvrs: [],
      cameras: []
    }
  }),
  
  actions: {
    async checkAuth() {
      try {
        const response = await axios.get('/api/v1/auth/status');
        this.user = response.data.user;
        this.csrfToken = response.data.csrf_token;
        axios.defaults.headers.common['X-CSRFToken'] = this.csrfToken;
        return true;
      } catch (error) {
        this.user = null;
        return false;
      }
    },

    async fetchDevices() {
      const response = await axios.get('/api/v1/devices');
      this.devices = response.data;
    },

    initSocket() {
      const socket = io();

      socket.on('connect', () => { this.uiOnline = true; });
      socket.on('disconnect', () => { this.uiOnline = false; this.mqttOnline = false; });
      
      socket.on('gateway_status', (data) => {
        this.mqttOnline = data.mqtt;
      });

      // Reactive payload handling!
      socket.on('state_change', (data) => {
        let collection = [];
        if (data.type === 'cameras') collection = this.devices.cameras;
        else if (data.type === 'switches') collection = this.devices.switches;
        else if (data.type === 'nvrs') collection = this.devices.nvrs;

        const device = collection.find(d => d.id === data.id);
        if (device) {
          device.status = data.status;
        }
      });
    }
  }
})
