<template>
  <div>
    <h5 class="fw-bold mb-3">가입한 상품들</h5>

    <p v-if="errorMsg" class="text-danger fw-semibold mb-2">{{ errorMsg }}</p>
    <div v-if="loading" class="text-muted">불러오는 중...</div>

    <div v-else>
      <div v-if="joinedProducts.length === 0" class="text-muted">
        아직 가입한 상품이 없습니다.
      </div>

      <div v-else class="mb-3">
        <div v-for="(p, idx) in joinedProducts" :key="p.id">
          {{ idx + 1 }}:
          <RouterLink :to="`/products/${p.id}`">
            ({{ p.type_label || p.product_type_label || p.product_type }})
            {{ p.kor_co_nm }} - {{ p.fin_prdt_nm }}
          </RouterLink>
        </div>
      </div>

      <h5 v-if="joinedProducts.length > 0" class="fw-bold mt-4">가입한 상품 금리</h5>

      <!-- 페이지네이션 -->
      <div
        v-if="joinedProducts.length > 0"
        class="d-flex justify-content-between align-items-center mb-2"
      >
        <span class="text-muted small">
          {{ currentPage + 1 }} / {{ totalPages }} 페이지 (한 페이지당 4개)
        </span>

        <div class="d-flex gap-2">
          <button
            class="btn btn-sm btn-outline-secondary"
            @click="prevPage"
            :disabled="currentPage === 0"
          >
            이전
          </button>
          <button
            class="btn btn-sm btn-outline-secondary"
            @click="nextPage"
            :disabled="currentPage >= totalPages - 1"
          >
            다음
          </button>
        </div>
      </div>

      <!-- 차트 -->
      <div v-if="joinedProducts.length > 0" class="border rounded p-3 chart-wrap">
        <canvas ref="chartCanvas"></canvas>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from "vue"
import { RouterLink } from "vue-router"
import Chart from "chart.js/auto"

import http from "@/api/http"
import { fetchProductDetail } from "@/api/products"

const loading = ref(false)
const errorMsg = ref("")
const joinedProducts = ref([])

const pageSize = 4
const currentPage = ref(0)

const totalPages = computed(() => {
  const n = joinedProducts.value.length
  return Math.max(1, Math.ceil(n / pageSize))
})

const pageItems = computed(() => {
  const start = currentPage.value * pageSize
  return joinedProducts.value.slice(start, start + pageSize)
})


const chartCanvas = ref(null)
let chartInstance = null

function prevPage() {
  if (currentPage.value > 0) currentPage.value -= 1
}

function nextPage() {
  if (currentPage.value < totalPages.value - 1) currentPage.value += 1
}


function buildFixedFourSlots(items) {
  const fixedLabels = []
  const fixedBase = []
  const fixedMax = []

  for (let i = 0; i < pageSize; i += 1) {
    const p = items[i]
    if (!p) {
      fixedLabels.push("")        
      fixedBase.push(null)
      fixedMax.push(null)
      continue
    }

    const opts = Array.isArray(p.options) ? p.options : []
    let base = null
    let max = null

    for (const o of opts) {
      const b = typeof o.intr_rate === "number" ? o.intr_rate : null
      const m = typeof o.intr_rate2 === "number" ? o.intr_rate2 : null
      if (b !== null) base = base === null ? b : Math.max(base, b)
      if (m !== null) max = max === null ? m : Math.max(max, m)
    }

    const name = p.fin_prdt_nm || ""
    const label =
      name.length > 14 ? [name.slice(0, 14), name.slice(14)] : name

    fixedLabels.push(label)
    fixedBase.push(base ?? 0)
    fixedMax.push(max ?? 0)
  }

  return { fixedLabels, fixedBase, fixedMax }
}

async function drawChart() {
  await nextTick()
  if (!chartCanvas.value) return

  if (chartInstance) {
    chartInstance.destroy()
    chartInstance = null
  }

  const { fixedLabels, fixedBase, fixedMax } = buildFixedFourSlots(pageItems.value)

  chartInstance = new Chart(chartCanvas.value, {
    type: "bar",
    data: {
      labels: fixedLabels,
      datasets: [
        {
          label: "기본 금리",
          data: fixedBase,
        },
        {
          label: "최고 우대금리",
          data: fixedMax,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false, 
      animation: false,
      plugins: {
        legend: { position: "top" },
        tooltip: { enabled: true },
      },
      scales: {
        x: {
          stacked: false,
          ticks: {
            maxRotation: 0,
            minRotation: 0,
            autoSkip: false, 
          },
        },
        y: {
          beginAtZero: true,
        },
      },
      datasets: {
        bar: {
          categoryPercentage: 0.7,
          barPercentage: 0.9,
        },
      },
    },
  })
}

async function loadJoinedProducts() {
  loading.value = true
  errorMsg.value = ""

  try {
    const me = await http.get("/api/accounts/profile/")
    const ids = Array.isArray(me.data?.joined_products) ? me.data.joined_products : []

    if (ids.length === 0) {
      joinedProducts.value = []
      currentPage.value = 0
      return
    }

    const details = await Promise.all(ids.map((id) => fetchProductDetail(id)))

    joinedProducts.value = details
    currentPage.value = 0
  } catch (e) {
    errorMsg.value = "가입한 상품 정보를 불러오지 못했습니다."
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadJoinedProducts()
  if (joinedProducts.value.length > 0) {
    await drawChart()
  }
})

watch([currentPage, joinedProducts], async () => {
  if (joinedProducts.value.length === 0) return
  if (currentPage.value > totalPages.value - 1) currentPage.value = totalPages.value - 1
  await drawChart()
})

onBeforeUnmount(() => {
  if (chartInstance) {
    chartInstance.destroy()
    chartInstance = null
  }
})
</script>

<style scoped>
.chart-wrap {
  height: 360px;
}
</style>
