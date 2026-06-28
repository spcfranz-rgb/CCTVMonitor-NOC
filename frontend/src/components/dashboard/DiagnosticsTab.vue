<template>
  <div class="row g-4">
    <div class="col-lg-6">
      <PingTraceTool />
    </div>
    <div class="col-lg-6">
      <SpeedtestTool />
    </div>
  </div>
</template>

<script setup>
import PingTraceTool from '../diagnostics/PingTraceTool.vue'
import SpeedtestTool from '../diagnostics/SpeedtestTool.vue'
</script>
