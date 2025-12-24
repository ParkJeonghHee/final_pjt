<template>
  <div class="route-panel card shadow-sm" v-if="place">
    <div class="card-body p-3">
      <div class="d-flex justify-content-between align-items-start">
        <div>
          <div class="fw-bold">{{ place.name }}</div>
          <div class="small text-muted">{{ place.address }}</div>
        </div>
        <button class="btn btn-sm btn-light" @click="$emit('close')" aria-label="닫기">
          <i class="bi bi-x"></i>
        </button>
      </div>

      <div class="btn-group w-100 mt-3" role="group" aria-label="경로 옵션">
        <button
          class="btn btn-sm"
          :class="mode==='car' ? 'btn-primary' : 'btn-outline-primary'"
          @click="$emit('update:mode', 'car')"
        >
          자동차
        </button>
        <button
          class="btn btn-sm"
          :class="mode==='transit' ? 'btn-primary' : 'btn-outline-primary'"
          @click="$emit('update:mode', 'transit')"
        >
          대중교통
        </button>
      </div>

      <div class="mt-3 small">
        <div class="d-flex justify-content-between">
          <span class="text-muted">거리</span>
          <span class="fw-semibold">{{ info?.distanceText || "-" }}</span>
        </div>
        <div class="d-flex justify-content-between mt-1">
          <span class="text-muted">시간</span>
          <span class="fw-semibold">{{ info?.durationText || "-" }}</span>
        </div>
      </div>

      <button class="btn btn-success btn-sm w-100 mt-3" @click="$emit('search-route')">
        경로 검색
      </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  place: Object,
  mode: { type: String, default: "car" },
  info: Object,
})
defineEmits(["close", "update:mode", "search-route"])
</script>

<style scoped>
.route-panel {
  position: absolute;
  top: 12px;
  left: 12px;
  width: 360px;
  max-width: calc(100% - 24px);
  border-radius: 14px;
  z-index: 50;
}
</style>
