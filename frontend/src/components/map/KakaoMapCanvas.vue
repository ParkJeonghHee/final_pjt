<template>
  <div class="map-area">
    <div class="map-canvas" ref="el"></div>
    <slot />
  </div>
</template>

<script setup>
import { ref, defineExpose } from "vue"
const el = ref(null)
defineExpose({ el })
</script>

<style scoped>
.map-area {
  position: relative;
  border-radius: 14px;
  overflow: hidden;
  border: 1px solid #eef1f3;
  height: 100%;
  min-height: 0;
  background: linear-gradient(180deg, #fbfaf9 0%, #f7f6f5 100%);
}
.map-canvas {
  width: 100%;
  height: 100%;
}
</style>
