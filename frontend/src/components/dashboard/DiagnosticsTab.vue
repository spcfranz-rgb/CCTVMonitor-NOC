<!--
Copyright (c) 2026 Timothy Franz. All Rights Reserved.

This file is part of Project Lighthouse.
Unauthorized copying of this file, via any medium, is strictly prohibited.
Proprietary and confidential.
-->

<template>
  <div class="row g-4">
    
    <div v-if="canRunDiagnostics" class="col-lg-6">
      <PingTraceTool />
    </div>
    
    <div :class="canRunDiagnostics ? 'col-lg-6' : 'col-12'">
      <SpeedtestTool />
    </div>

  </div>
</template>

<script setup>
import { computed } from 'vue'
import PingTraceTool from '../diagnostics/PingTraceTool.vue'
import SpeedtestTool from '../diagnostics/SpeedtestTool.vue'
import { useSystemStore } from '../../stores/systemStore'

const store = useSystemStore()

// RBAC: Only admins and operators can access active network probes
const canRunDiagnostics = computed(() => {
  return ['admin', 'operator'].includes(store.user?.role)
})
</script>
