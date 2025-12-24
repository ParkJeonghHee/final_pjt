<template>
  <div>
    <h5 class="fw-bold mb-4">가입한 상품들</h5>

    <section class="mb-4">
      <div class="section-header deposit">
        <span class="badge bg-primary me-2">예금·적금</span>
        <span class="fw-bold">가입한 예금·적금 상품</span>
      </div>

      <p v-if="errorMsg" class="text-danger fw-semibold mb-2">{{ errorMsg }}</p>
      <div v-if="loading" class="text-muted">불러오는 중...</div>

      <div v-else>
        <div v-if="joinedProducts.length === 0" class="text-muted">
          가입한 예금/적금 상품이 없습니다.
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

        <h5 v-if="joinedProducts.length > 0" class="fw-bold mt-4">가입한 예금·적금 상품 금리</h5>

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

        <div v-if="joinedProducts.length > 0" class="border rounded p-3 chart-wrap">
          <canvas ref="chartCanvas"></canvas>
        </div>
      </div>
    </section>

    <section>
      <div class="section-header loan">
        <span class="badge bg-success me-2">대출</span>
        <span class="fw-bold">가입한 대출 상품</span>
      </div>

      <p v-if="loansErrorMsg" class="text-danger fw-semibold mb-2">{{ loansErrorMsg }}</p>
      <div v-if="loansLoading" class="text-muted">불러오는 중...</div>

      <div v-else>
        <div v-if="joinedLoans.length === 0" class="text-muted">
          가입한 대출 상품이 없습니다.
        </div>
        <div v-else class="mb-2">
          <div v-for="(loan, idx) in joinedLoans" :key="loan.fin_prdt_cd">
            {{ idx + 1 }}:
            <RouterLink
              :to="{ path: `/loans/${loan.fin_prdt_cd}`, query: { category: loan.category || 'credit' } }"
            >
              ({{ loan.categoryLabel }}) {{ loan.kor_co_nm || '-' }} - {{ loan.fin_prdt_nm || '-' }}
            </RouterLink>
          </div>
        </div>

        <h5 v-if="joinedLoans.length > 0" class="fw-bold mt-4">가입한 대출 상품 금리</h5>

        <div
          v-if="joinedLoans.length > 0"
          class="d-flex justify-content-between align-items-center mb-2"
        >
          <span class="text-muted small">
            {{ loanPage + 1 }} / {{ loanTotalPages }} 페이지 (한 페이지당 4개)
          </span>

          <div class="d-flex gap-2">
            <button
              class="btn btn-sm btn-outline-secondary"
              @click="prevLoanPage"
              :disabled="loanPage === 0"
            >
              이전
            </button>
            <button
              class="btn btn-sm btn-outline-secondary"
              @click="nextLoanPage"
              :disabled="loanPage >= loanTotalPages - 1"
            >
              다음
            </button>
          </div>
        </div>

        <div v-if="joinedLoans.length > 0" class="border rounded p-3 chart-wrap">
          <canvas ref="loanChartCanvas"></canvas>
        </div>
      </div>
    </section>
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

const joinedLoans = ref([])
const loansLoading = ref(false)
const loansErrorMsg = ref("")
const loanPage = ref(0)
const loanChartCanvas = ref(null)
let loanChartInstance = null

const loanStorageKey = "loan_joined"

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

function splitByMaxLenWordwise(text, maxLen, maxLines = 3) {
  const s = (text || "").trim()
  if (!s) return [""]

  const words = s.split(/\s+/)
  const lines = []
  let cur = ""

  for (const w of words) {
    if (w.length > maxLen) {
      if (cur) {
        lines.push(cur)
        cur = ""
      }
      let rest = w
      while (rest.length > maxLen && lines.length < maxLines) {
        lines.push(rest.slice(0, maxLen))
        rest = rest.slice(maxLen)
      }
      if (rest && lines.length < maxLines) cur = rest
      continue
    }

    const next = cur ? `${cur} ${w}` : w
    if (next.length <= maxLen) {
      cur = next
    } else {
      if (cur) lines.push(cur)
      cur = w
      if (lines.length >= maxLines - 1) break
    }
  }

  if (cur && lines.length < maxLines) lines.push(cur)

  if (lines.length > maxLines) {
    const head = lines.slice(0, maxLines)
    head[maxLines - 1] = head[maxLines - 1].slice(0, Math.max(0, maxLen - 1)) + "…"
    return head
  }

  return lines
}

function makeChartLabel(name, maxLen = 18) {
  if (!name) return ""

  const parenIdx = name.indexOf("(")
  if (parenIdx > 0) {
    const a = name.slice(0, parenIdx).trim()
    const b = name.slice(parenIdx).trim()
    const bLines = splitByMaxLenWordwise(b, maxLen, 2) 
    return [a, ...bLines]
  }

  if (name.length <= maxLen) return name
  const lines = splitByMaxLenWordwise(name, maxLen, 3)
  return lines.length === 1 ? lines[0] : lines
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
    const label = makeChartLabel(name, 18)

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
        { label: "기본 금리", data: fixedBase },
        { label: "최고 우대금리", data: fixedMax },
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
        y: { beginAtZero: true },
      },
      datasets: {
        bar: { categoryPercentage: 0.7, barPercentage: 0.9 },
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

function toLoanCategoryLabel(category) {
  if (category === "mortgage") return "주택담보대출"
  if (category === "renthouse") return "전세자금대출"
  return "주택담보대출"
}

function normalizeLoanEntries(raw) {
  if (!Array.isArray(raw)) return []
  return raw
    .map((item) => {
      if (typeof item === "string") {
        return { fin_prdt_cd: item, category: "mortgage" }
      }
      if (item && typeof item === "object") {
        return {
          fin_prdt_cd: item.fin_prdt_cd,
          category: item.category || "mortgage",
          kor_co_nm: item.kor_co_nm,
          fin_prdt_nm: item.fin_prdt_nm,
        }
      }
      return null
    })
    .filter((v) => v && v.fin_prdt_cd)
}

function loadLoanStorage() {
  try {
    const raw = localStorage.getItem(loanStorageKey)
    const parsed = raw ? JSON.parse(raw) : []
    const normalized = normalizeLoanEntries(parsed).filter((item) => item.category !== "credit")
    localStorage.setItem(loanStorageKey, JSON.stringify(normalized))
    return normalized
  } catch (e) {
    return []
  }
}

async function loadJoinedLoans() {
  loansLoading.value = true
  loansErrorMsg.value = ""

  try {
    const stored = loadLoanStorage()
    if (stored.length === 0) {
      joinedLoans.value = []
      return
    }

    const details = await Promise.all(
      stored.map(async (item) => {
        try {
          const res = await http.get(`/api/loans/${item.fin_prdt_cd}/`, {
            params: { category: item.category || "mortgage" },
          })
          return {
            ...item,
            ...res.data,
            categoryLabel: toLoanCategoryLabel(item.category),
          }
        } catch (e) {
          return { ...item, categoryLabel: toLoanCategoryLabel(item.category) }
        }
      })
    )

    joinedLoans.value = details
  } catch (e) {
    loansErrorMsg.value = "가입한 대출 상품 정보를 불러오지 못했습니다."
  } finally {
    loansLoading.value = false
  }
}

const loanTotalPages = computed(() => {
  const n = joinedLoans.value.length
  return Math.max(1, Math.ceil(n / pageSize))
})

const loanPageItems = computed(() => {
  const start = loanPage.value * pageSize
  return joinedLoans.value.slice(start, start + pageSize)
})

function prevLoanPage() {
  if (loanPage.value > 0) loanPage.value -= 1
}

function nextLoanPage() {
  if (loanPage.value < loanTotalPages.value - 1) loanPage.value += 1
}

function buildLoanSlots(items) {
  const fixedLabels = []
  const fixedMin = []
  const fixedMax = []

  for (let i = 0; i < pageSize; i += 1) {
    const p = items[i]
    if (!p) {
      fixedLabels.push("")
      fixedMin.push(null)
      fixedMax.push(null)
      continue
    }

    const { minRate, maxRate } = getLoanRateSummary(p)

    const name = p.fin_prdt_nm || ""
    const label = makeChartLabel(name, 18)

    fixedLabels.push(label)
    fixedMin.push(Number.isFinite(minRate) ? minRate : null)
    fixedMax.push(Number.isFinite(maxRate) ? maxRate : null)
  }

  return { fixedLabels, fixedMin, fixedMax }
}

function parseLoanRate(value) {
  if (value === null || value === undefined || value === "") return null
  if (typeof value === "string") {
    const trimmed = value.trim()
    if (trimmed === "-" || trimmed === "") return null
    const cleaned = trimmed.replace("%", "").replace(",", "")
    const num = Number(cleaned)
    return Number.isFinite(num) ? num : null
  }
  const num = Number(value)
  return Number.isFinite(num) ? num : null
}

function getLoanRateSummary(product) {
  const directMin = parseLoanRate(product?.lend_rate_min)
  const directMax = parseLoanRate(product?.lend_rate_max)
  if (directMin !== null || directMax !== null) {
    return { minRate: directMin, maxRate: directMax }
  }

  const options = Array.isArray(product?.options) ? product.options : []
  const mins = []
  const maxs = []

  for (const opt of options) {
    const minVal = parseLoanRate(opt?.lend_rate_min)
    const maxVal = parseLoanRate(opt?.lend_rate_max)
    if (minVal !== null) mins.push(minVal)
    if (maxVal !== null) maxs.push(maxVal)
  }

  return {
    minRate: mins.length ? Math.min(...mins) : null,
    maxRate: maxs.length ? Math.max(...maxs) : null,
  }
}

function hasAnyLoanRate(items) {
  return items.some((item) => {
    if (!item) return false
    const { minRate, maxRate } = getLoanRateSummary(item)
    return Number.isFinite(minRate) || Number.isFinite(maxRate)
  })
}

async function drawLoanChart() {
  await nextTick()
  if (!loanChartCanvas.value) return

  if (!hasAnyLoanRate(loanPageItems.value)) {
    if (loanChartInstance) {
      loanChartInstance.destroy()
      loanChartInstance = null
    }
    return
  }

  if (loanChartInstance) {
    loanChartInstance.destroy()
    loanChartInstance = null
  }

  const { fixedLabels, fixedMin, fixedMax } = buildLoanSlots(loanPageItems.value)

  loanChartInstance = new Chart(loanChartCanvas.value, {
    type: "bar",
    data: {
      labels: fixedLabels,
      datasets: [
        { label: "최저 금리", data: fixedMin },
        { label: "최고 금리", data: fixedMax },
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
        y: { beginAtZero: true },
      },
      datasets: {
        bar: { categoryPercentage: 0.7, barPercentage: 0.9 },
      },
    },
  })
}

onMounted(async () => {
  await loadJoinedProducts()
  await loadJoinedLoans()
  if (joinedProducts.value.length > 0) await drawChart()
  if (joinedLoans.value.length > 0) await drawLoanChart()
})

watch([currentPage, joinedProducts], async () => {
  if (joinedProducts.value.length === 0) return
  if (currentPage.value > totalPages.value - 1) currentPage.value = totalPages.value - 1
  await drawChart()
})

watch([loanPage, joinedLoans], async () => {
  if (joinedLoans.value.length === 0) return
  if (loanPage.value > loanTotalPages.value - 1) loanPage.value = loanTotalPages.value - 1
  await drawLoanChart()
})

onBeforeUnmount(() => {
  if (chartInstance) {
    chartInstance.destroy()
    chartInstance = null
  }
  if (loanChartInstance) {
    loanChartInstance.destroy()
    loanChartInstance = null
  }
})
</script>

<style scoped>
.chart-wrap {
  height: 360px;
}

.section-header {
  display: flex;
  align-items: center;
  padding: 10px 14px;
  border-radius: 6px;
  margin-bottom: 12px;
  font-size: 1rem;
  border: 1px solid #e9ecef;
}

.section-header.deposit {
  background-color: rgba(13, 110, 253, 0.06);
  border-left: 5px solid #0d6efd;
}

.section-header.loan {
  background-color: rgba(25, 135, 84, 0.06);
  border-left: 5px solid #198754;
}
</style>
