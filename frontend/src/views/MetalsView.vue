<template>
  <main class="container my-5">
    <div class="p-4 border rounded bg-white">
      <h4 class="fw-bold mb-3">금/은 가격 변동</h4>

      <!-- 금/은 선택 -->
      <div class="d-flex gap-2 mb-3">
        <button
          type="button"
          class="btn"
          :class="asset === 'gold' ? 'btn-success' : 'btn-outline-success'"
          @click="asset = 'gold'"
        >
          금
        </button>

        <button
          type="button"
          class="btn"
          :class="asset === 'silver' ? 'btn-success' : 'btn-outline-success'"
          @click="asset = 'silver'"
        >
          은
        </button>
      </div>

      <!-- 날짜 선택 + 조회 -->
      <div class="row g-2 align-items-end mb-3">
        <div class="col-md-4">
          <label class="form-label mb-1">시작일</label>
          <input class="form-control" type="date" v-model="start" />
        </div>

        <div class="col-md-4">
          <label class="form-label mb-1">종료일</label>
          <input class="form-control" type="date" v-model="end" />
        </div>

        <div class="col-md-4 d-flex gap-2">
          <button type="button" class="btn btn-success w-50" @click="onSearch">조회</button>
          <button type="button" class="btn btn-outline-secondary w-50" @click="onReset">
            초기화
          </button>
        </div>
      </div>

      <!-- 에러 문구 -->
      <p v-if="errorMsg" class="text-danger fw-semibold mb-3">
        {{ errorMsg }}
      </p>

      <!-- 차트 -->
      <div class="border rounded p-3">
        <canvas ref="chartEl"></canvas>
      </div>

      <p class="text-muted mt-2 mb-0" v-if="count !== null">
        데이터 개수: {{ count }}개
      </p>
    </div>

    <div class="p-4 border rounded bg-white mt-4">
      <div class="d-flex flex-wrap align-items-center justify-content-between gap-3 mb-3">
        <h4 class="fw-bold mb-0">환율·금리 추이</h4>
        <div class="d-flex align-items-center gap-2">
          <label class="form-label mb-0 small text-muted">기간</label>
          <select class="form-select form-select-sm w-auto" v-model="years">
            <option :value="1">최근 1년</option>
            <option :value="3">최근 3년</option>
            <option :value="5">최근 5년</option>
            <option :value="10">최근 10년</option>
          </select>
        </div>
      </div>

      <p v-if="marketError" class="text-danger fw-semibold mb-3">
        {{ marketError }}
      </p>

      <div class="macro-grid">
        <div class="macro-card">
          <div class="macro-header">
            <div>
              <p class="macro-title">USD/KRW</p>
              <p class="macro-value">{{ formatNumber(latest.usd) }}</p>
              <p class="macro-sub">달러 환율</p>
            </div>
          </div>
          <div class="macro-chart">
            <canvas ref="usdChartEl"></canvas>
          </div>
          <p v-if="marketSeries.usd.length === 0" class="macro-empty">데이터 없음</p>
        </div>

        <div class="macro-card">
          <div class="macro-header">
            <div>
              <p class="macro-title">JPY/KRW</p>
              <p class="macro-value">{{ formatNumber(latest.jpy) }}</p>
              <p class="macro-sub">엔 환율 (100엔)</p>
            </div>
          </div>
          <div class="macro-chart">
            <canvas ref="jpyChartEl"></canvas>
          </div>
          <p v-if="marketSeries.jpy.length === 0" class="macro-empty">데이터 없음</p>
        </div>

        <div class="macro-card">
          <div class="macro-header">
            <div>
              <p class="macro-title">KR 기준금리</p>
              <p class="macro-value">{{ formatPercent(latest.baseRate) }}</p>
              <p class="macro-sub">대한민국 기준금리</p>
            </div>
          </div>
          <div class="macro-chart">
            <canvas ref="baseRateChartEl"></canvas>
          </div>
          <p v-if="marketSeries.baseRate.length === 0" class="macro-empty">데이터 없음</p>
        </div>

        <div class="macro-card">
          <div class="macro-header">
            <div>
              <p class="macro-title">국채 3년</p>
              <p class="macro-value">{{ formatPercent(latest.bond3y) }}</p>
              <p class="macro-sub">금리 기준 지표</p>
            </div>
          </div>
          <div class="macro-chart">
            <canvas ref="bond3yChartEl"></canvas>
          </div>
          <p v-if="marketSeries.bond3y.length === 0" class="macro-empty">데이터 없음</p>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from "vue"
import { Chart } from "chart.js/auto"
import { fetchMetalSeries } from "@/api/metals"
import { fetchMarketHistory } from "@/api/market"

const asset = ref("gold")
const start = ref("")
const end = ref("")
const errorMsg = ref("")
const count = ref(null)
const years = ref(3)
const marketError = ref("")
const marketSeries = ref({
  usd: [],
  jpy: [],
  baseRate: [],
  bond3y: [],
})
const latest = ref({
  usd: null,
  jpy: null,
  baseRate: null,
  bond3y: null,
})

const chartEl = ref(null)
const usdChartEl = ref(null)
const jpyChartEl = ref(null)
const baseRateChartEl = ref(null)
const bond3yChartEl = ref(null)
let chartInstance = null
const marketCharts = {
  usd: null,
  jpy: null,
  baseRate: null,
  bond3y: null,
}

function destroyChart() {
  if (chartInstance) {
    chartInstance.destroy()
    chartInstance = null
  }
}

function renderChart(labels, data) {
  destroyChart()
  const ctx = chartEl.value.getContext("2d")
  const isGold = asset.value === "gold"
  const lineColor = isGold ? "#d9a441" : "#2563eb"
  const glowColor = isGold ? "rgba(217, 164, 65, 0.18)" : "rgba(37, 99, 235, 0.18)"
  const gradient = ctx.createLinearGradient(0, 0, 0, chartEl.value.height || 300)
  gradient.addColorStop(0, glowColor)
  gradient.addColorStop(1, "rgba(255, 255, 255, 0)")

  chartInstance = new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: isGold ? "Gold Close/Last" : "Silver Close/Last",
          data,
          borderColor: lineColor,
          backgroundColor: gradient,
          fill: true,
          tension: 0.35,
          pointRadius: 2,
          pointHoverRadius: 5,
          pointBackgroundColor: lineColor,
          pointBorderWidth: 0,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          display: true,
          labels: { boxWidth: 14, usePointStyle: true, pointStyle: "circle" },
        },
        tooltip: {
          callbacks: {
            label: (ctx) => ` ${ctx.parsed.y.toLocaleString()}`,
          },
        },
      },
      scales: {
        x: {
          display: true,
          grid: { display: false },
          ticks: { maxRotation: 0, autoSkip: true, maxTicksLimit: 12 },
        },
        y: {
          display: true,
          grid: { color: "rgba(15, 23, 42, 0.08)" },
          ticks: {
            callback: (v) => Number(v).toLocaleString(),
          },
        },
      },
    },
  })
}

function formatNumber(value, digits = 2) {
  const num = Number(value)
  if (!Number.isFinite(num)) return "-"
  return num.toLocaleString(undefined, { minimumFractionDigits: digits, maximumFractionDigits: digits })
}

function formatPercent(value) {
  const num = Number(value)
  if (!Number.isFinite(num)) return "-"
  return `${num.toFixed(2)}%`
}

function destroyMarketCharts() {
  Object.keys(marketCharts).forEach((key) => {
    if (marketCharts[key]) {
      marketCharts[key].destroy()
      marketCharts[key] = null
    }
  })
}

function renderMarketChart(key, el, labels, data, lineColor) {
  if (!el) {
    return
  }
  if (marketCharts[key]) {
    marketCharts[key].destroy()
    marketCharts[key] = null
  }

  const ctx = el.getContext("2d")
  const gradient = ctx.createLinearGradient(0, 0, 0, el.height || 240)
  gradient.addColorStop(0, `${lineColor}33`)
  gradient.addColorStop(1, "rgba(255, 255, 255, 0)")

  marketCharts[key] = new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          data,
          borderColor: lineColor,
          backgroundColor: gradient,
          fill: true,
          tension: 0.3,
          pointRadius: 0,
          pointHoverRadius: 4,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => ` ${ctx.parsed.y.toLocaleString()}`,
          },
        },
      },
      scales: {
        x: {
          display: false,
        },
        y: {
          display: true,
          grid: { color: "rgba(15, 23, 42, 0.08)" },
          ticks: {
            callback: (v) => Number(v).toLocaleString(),
          },
        },
      },
    },
  })
}

async function loadMarketHistory() {
  marketError.value = ""
  try {
    const data = await fetchMarketHistory(years.value)
    const series = data.series || {}

    marketSeries.value = {
      usd: series.usd_krw || [],
      jpy: series.jpy_krw_100 || [],
      baseRate: series.base_rate || [],
      bond3y: series.bond_3y || [],
    }

    const pickLast = (list) => (list.length ? list[list.length - 1].value : null)
    latest.value = {
      usd: pickLast(marketSeries.value.usd),
      jpy: pickLast(marketSeries.value.jpy),
      baseRate: pickLast(marketSeries.value.baseRate),
      bond3y: pickLast(marketSeries.value.bond3y),
    }

    await nextTick()
    renderMarketChart(
      "usd",
      usdChartEl.value,
      marketSeries.value.usd.map((x) => x.date),
      marketSeries.value.usd.map((x) => x.value),
      "#2563eb",
    )
    renderMarketChart(
      "jpy",
      jpyChartEl.value,
      marketSeries.value.jpy.map((x) => x.date),
      marketSeries.value.jpy.map((x) => x.value),
      "#0ea5e9",
    )
    renderMarketChart(
      "baseRate",
      baseRateChartEl.value,
      marketSeries.value.baseRate.map((x) => x.date),
      marketSeries.value.baseRate.map((x) => x.value),
      "#10b981",
    )
    renderMarketChart(
      "bond3y",
      bond3yChartEl.value,
      marketSeries.value.bond3y.map((x) => x.date),
      marketSeries.value.bond3y.map((x) => x.value),
      "#f97316",
    )
  } catch (err) {
    marketError.value = "시장 데이터를 불러오는 중 오류가 발생했습니다."
    destroyMarketCharts()
  }
}

async function loadSeries() {
  errorMsg.value = ""

  // start > end 인 경우
  if (start.value && end.value && start.value > end.value) {
    errorMsg.value = "선택된 조건에 해당하는 데이터가 없습니다."
    destroyChart()
    count.value = null
    return
  }

  try {
    const res = await fetchMetalSeries({
      asset: asset.value,
      start: start.value,
      end: end.value,
    })

    const series = res.data.series || []

    // 조건에 맞는 데이터가 없는 경우
    if (series.length === 0) {
      errorMsg.value = "선택된 조건에 해당하는 데이터가 없습니다."
      destroyChart()
      count.value = null
      return
    }

    // 정상 데이터인 경우만 차트 그림
    count.value = res.data.count ?? series.length

    const labels = series.map((x) => x.date)
    const data = series.map((x) => x.price)

    renderChart(labels, data)
  } catch (err) {
    // 서버/네트워크 에러 등 "진짜 오류" 상황
    errorMsg.value = "데이터를 불러오는 중 오류가 발생하였습니다."
    destroyChart()
    count.value = null
  }
}


function onSearch() {
  loadSeries()
}

function onReset() {
  start.value = ""
  end.value = ""
  errorMsg.value = ""
  loadSeries()
}

onMounted(() => {
  loadSeries()
  loadMarketHistory()
})

watch(asset, () => {
  loadSeries()
})

watch(years, () => {
  loadMarketHistory()
})
</script>

<style scoped>
.macro-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.macro-card {
  border: 1px solid rgba(148, 163, 184, 0.35);
  border-radius: 16px;
  padding: 16px;
  background: #fff;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.08);
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.macro-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.macro-title {
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: #64748b;
  margin: 0;
}

.macro-value {
  font-size: 1.3rem;
  font-weight: 700;
  color: #0f172a;
  margin: 2px 0 0;
}

.macro-sub {
  font-size: 0.8rem;
  color: #475569;
  margin: 0;
}

.macro-chart {
  position: relative;
  height: 160px;
}

.macro-empty {
  margin: 0;
  font-size: 0.85rem;
  color: #94a3b8;
}

@media (max-width: 991.98px) {
  .macro-grid {
    grid-template-columns: 1fr;
  }
  .macro-chart {
    height: 180px;
  }
}
</style>
