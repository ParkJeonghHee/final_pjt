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
  </main>
</template>

<script setup>
import { ref, onMounted, watch } from "vue"
import { Chart } from "chart.js/auto"
import { fetchMetalSeries } from "@/api/metals"

const asset = ref("gold")
const start = ref("")
const end = ref("")
const errorMsg = ref("")
const count = ref(null)

const chartEl = ref(null)
let chartInstance = null

function destroyChart() {
  if (chartInstance) {
    chartInstance.destroy()
    chartInstance = null
  }
}

function renderChart(labels, data) {
  destroyChart()
  chartInstance = new Chart(chartEl.value, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: asset.value === "gold" ? "Gold Close/Last" : "Silver Close/Last",
          data,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: { legend: { display: true } },
      scales: {
        x: { display: true },
        y: { display: true },
      },
    },
  })
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
})

watch(asset, () => {
  loadSeries()
})
</script>
