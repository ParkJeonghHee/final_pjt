<template>
  <aside class="card side-card">
    <h5 class="card-title">은행 찾기</h5>

    <div class="mb-3">
      <div class="input-group input-group-sm">
        <span class="input-group-text"><i class="bi bi-search"></i></span>
        <input
          :value="keyword"
          class="form-control"
          placeholder="은행명 또는 주소 검색"
          @input="$emit('update:keyword', $event.target.value)"
          @keyup.enter="$emit('search')"
        />
      </div>
    </div>

    <div class="divider"></div>

    <div class="mb-2">
      <label class="form-label small text-muted">광역시/도</label>
      <select
        :value="selectedSido"
        class="form-select form-select-sm"
        @change="$emit('update:selectedSido', $event.target.value)"
      >
        <option value="">선택</option>
        <option v-for="s in sidos" :key="s" :value="s">{{ s }}</option>
      </select>
    </div>

    <div class="mb-2">
      <label class="form-label small text-muted">시/군/구</label>
      <select
        :value="selectedSigungu"
        class="form-select form-select-sm"
        :disabled="!selectedSido"
        @change="$emit('update:selectedSigungu', $event.target.value)"
      >
        <option value="">선택</option>
        <option v-for="g in sigungus" :key="g" :value="g">{{ g }}</option>
      </select>
    </div>

    <div class="mb-3">
      <label class="form-label small text-muted">은행</label>
      <select
        :value="selectedBank"
        class="form-select form-select-sm"
        @change="$emit('update:selectedBank', $event.target.value)"
      >
        <option value="">선택</option>
        <option v-for="b in banks" :key="b" :value="b">{{ b }}</option>
      </select>
    </div>

    <button class="btn btn-success w-100 btn-sm" @click="$emit('search')">
      <i class="bi bi-search me-1"></i> 찾기
    </button>

    <div class="hint">거리가 가까운 곳 먼저 조회됩니다.</div>

    <div class="result-head">
      <div class="small fw-semibold">검색 결과 ({{ results.length }})</div>
      <select
        :value="sortMode"
        class="form-select form-select-sm sort"
        @change="$emit('update:sortMode', $event.target.value)"
      >
        <option value="distance">거리순</option>
        <option value="name">이름순</option>
      </select>
    </div>

    <div class="result-list">
      <div v-if="!results.length" class="empty-note text-muted small">
        검색 결과가 없습니다.
      </div>

      <button
        v-for="place in sortedResults"
        :key="place.id"
        type="button"
        class="result-item"
        :class="{ active: selectedPlace?.id === place.id }"
        @click="$emit('select-place', place)"
      >
        <div class="d-flex align-items-start gap-2">
          <div class="avatar"><i class="bi bi-bank"></i></div>

          <div class="flex-grow-1">
            <div class="d-flex justify-content-between align-items-start">
              <div>
                <div class="name">{{ place.name }}</div>
                <div class="addr">{{ place.address }}</div>
              </div>

              <div class="text-end">
                <div class="dist">{{ formatKm(place.distanceKm) }}</div>
                <div class="more">자세히 보기 →</div>
              </div>
            </div>
          </div>
        </div>
      </button>

      <button
        v-if="results.length"
        class="btn btn-outline-secondary w-100 btn-sm mt-2"
        @click="$emit('clear')"
      >
        결과/검색 지우기
      </button>
    </div>
  </aside>
</template>

<script setup>
import { computed } from "vue"

const props = defineProps({
  keyword: String,
  selectedSido: String,
  selectedSigungu: String,
  selectedBank: String,
  sidos: { type: Array, default: () => [] },
  sigungus: { type: Array, default: () => [] },
  banks: { type: Array, default: () => [] },
  results: { type: Array, default: () => [] },
  selectedPlace: Object,
  sortMode: { type: String, default: "distance" },
})

defineEmits([
  "update:keyword",
  "update:selectedSido",
  "update:selectedSigungu",
  "update:selectedBank",
  "update:sortMode",
  "search",
  "select-place",
  "clear",
])

function formatKm(km) {
  if (km == null) return "-"
  return km < 1 ? `${Math.round(km * 1000)}m` : `${km.toFixed(1)}km`
}

const sortedResults = computed(() => {
  const list = [...props.results]
  if (props.sortMode === "name") return list.sort((a, b) => (a.name || "").localeCompare(b.name || ""))
  return list.sort((a, b) => (a.distanceKm ?? Infinity) - (b.distanceKm ?? Infinity))
})
</script>

<style scoped>
.side-card { padding: 18px; height: 100%; min-height: 0; display: flex; flex-direction: column; }
.card-title { font-weight: 800; margin: 0 0 10px; }
.divider { height: 1px; background: #eef1f3; margin: 12px 0; }
.hint { margin-top: 10px; font-size: 12px; color: #6b7280; background: #f8fafc; border: 1px solid #eef1f3; border-radius: 10px; padding: 10px 12px; }
.result-head { margin-top: 16px; display: flex; align-items: center; justify-content: space-between; gap: 10px; }
.sort { width: 120px; }
.result-list { margin-top: 10px; overflow-y: auto; padding-right: 6px; flex: 1; min-height: 0; }
.result-item { width: 100%; background: #fff; border: 1px solid rgba(16, 24, 40, 0.10); border-radius: 14px; padding: 12px; text-align: left; margin-bottom: 10px; }
.result-item.active { border-color: #198754; box-shadow: 0 14px 28px rgba(25, 135, 84, 0.16); }
.avatar { width: 44px; height: 44px; border-radius: 12px; background: #eef2ff; display: grid; place-items: center; color: #1d4ed8; flex: 0 0 auto; }
.name { font-weight: 800; font-size: 14px; }
.addr { font-size: 12px; color: #6b7280; margin-top: 2px; }
.dist { font-size: 12px; color: #6b7280; }
.more { font-size: 12px; color: #2563eb; margin-top: 6px; }
.result-list::-webkit-scrollbar { width: 10px; }
.result-list::-webkit-scrollbar-thumb { background: rgba(16, 24, 40, 0.10); border-radius: 8px; }
</style>
