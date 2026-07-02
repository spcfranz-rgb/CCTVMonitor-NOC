/*
 * Copyright (c) 2026 Timothy Franz. All Rights Reserved.
 *
 * This file is part of Project Lighthouse.
 * Unauthorized copying of this file, via any medium, is strictly prohibited.
 * Proprietary and confidential.
 */

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  build: {
    // Stage 1 build dumps directly into the folder Stage 2 expects
    outDir: 'dist',
    emptyOutDir: true
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true
      },
      '/socket.io': {
        target: 'http://127.0.0.1:5000',
        ws: true,
        changeOrigin: true
      },
      '/tunnel': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true
      }
    }
  }
})
