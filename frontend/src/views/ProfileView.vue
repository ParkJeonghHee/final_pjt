<template>
  <main class="container my-4">
    <div class="p-4 border rounded bg-white mb-3">
      <h4 class="fw-bold mb-0">{{ auth.username }} 님의 프로필</h4>
    </div>

    <div class="border-bottom mb-3 pb-2">
      <a
        href="#"
        class="text-decoration-none tab-link"
        :class="tab === 'info' ? 'fw-bold text-dark' : 'text-muted'"
        @click.prevent="switchTab('info')"
      >
        기본 정보 수정
      </a>
      <span class="divider"> | </span>

      <a
        href="#"
        class="text-decoration-none tab-link"
        :class="tab === 'portfolio' ? 'fw-bold text-dark' : 'text-muted'"
        @click.prevent="switchTab('portfolio')"
      >
        포트폴리오 수정
      </a>
      <span class="divider"> | </span>

      <a
        href="#"
        class="text-decoration-none tab-link"
        :class="tab === 'recommend' ? 'fw-bold text-dark' : 'text-muted'"
        @click.prevent="switchTab('recommend')"
      >
        상품 추천 받기
      </a>
      <span class="divider"> | </span>

      <a
        href="#"
        class="text-decoration-none tab-link"
        :class="tab === 'videos' ? 'fw-bold text-dark' : 'text-muted'"
        @click.prevent="switchTab('videos')"
      >
        관심 동영상
      </a>
    </div>

    <div class="p-4 border rounded bg-white">
      <template v-if="tab === 'info'">
        <h5 class="fw-bold mb-3">기본 정보 수정</h5>

        <div v-if="loading" class="text-muted">불러오는 중...</div>

        <div v-else>
          <p v-if="errorMsg" class="text-danger fw-semibold mb-3">
            {{ errorMsg }}
          </p>

          <p v-if="successMsg" class="text-success fw-semibold mb-3">
            {{ successMsg }}
          </p>

          <div class="mb-3">
            <label class="form-label">회원번호</label>
            <input class="form-control" :value="profile.id ?? ''" disabled />
          </div>

          <div class="mb-3">
            <label class="form-label">ID</label>
            <input class="form-control" :value="profile.username ?? ''" disabled />
          </div>

          <div class="mb-3 d-flex gap-2 align-items-end">
            <div class="flex-grow-1">
              <label class="form-label">Email</label>
              <input class="form-control" v-model="profile.email" placeholder="이메일을 설정해주세요" />
            </div>
            <button class="btn btn-primary" :disabled="savingField !== null" @click="onSaveField('email')">
              {{ savingField === "email" ? "수정 중..." : "수정하기" }}
            </button>
          </div>

          <div class="mb-3 d-flex gap-2 align-items-end">
            <div class="flex-grow-1">
              <label class="form-label">Nickname</label>
              <input class="form-control" v-model="profile.nickname" placeholder="닉네임을 설정해주세요" />
            </div>
            <button class="btn btn-primary" :disabled="savingField !== null" @click="onSaveField('nickname')">
              {{ savingField === "nickname" ? "수정 중..." : "수정하기" }}
            </button>
          </div>

          <div class="mb-3 d-flex gap-2 align-items-end">
            <div class="flex-grow-1">
              <label class="form-label">나이</label>
              <input class="form-control" v-model.number="profile.age" type="number" min="0" />
            </div>
            <button class="btn btn-primary" :disabled="savingField !== null" @click="onSaveField('age')">
              {{ savingField === "age" ? "수정 중..." : "수정하기" }}
            </button>
          </div>

          <div class="mb-3 d-flex gap-2 align-items-end">
            <div class="flex-grow-1">
              <label class="form-label">총 자산</label>
              <input class="form-control" v-model.number="profile.total_assets" type="number" min="0" />
            </div>
            <button class="btn btn-primary" :disabled="savingField !== null" @click="onSaveField('total_assets')">
              {{ savingField === "total_assets" ? "수정 중..." : "수정하기" }}
            </button>
          </div>

          <div class="mb-4 d-flex gap-2 align-items-end">
            <div class="flex-grow-1">
              <label class="form-label">월 소득</label>
              <input class="form-control" v-model.number="profile.income" type="number" min="0" />
            </div>
            <button class="btn btn-primary" :disabled="savingField !== null" @click="onSaveField('income')">
              {{ savingField === "income" ? "수정 중..." : "수정하기" }}
            </button>
          </div>

          <hr class="my-4" />

          <h5 class="fw-bold mb-2">가입한 상품들</h5>

          <div v-if="joinedProductsLoading" class="text-muted mb-2">
            가입한 상품 불러오는 중...
          </div>

          <div v-if="joinedErrorMsg" class="text-danger fw-semibold mb-2">
            {{ joinedErrorMsg }}
          </div>

          <div v-if="!joinedProductsLoading && joinedProducts.length === 0" class="text-muted mb-3">
            가입한 상품이 없습니다.
          </div>

          <div v-if="joinedProducts.length > 0" class="mb-3">
            <div v-for="(p, idx) in joinedProducts" :key="p.id" class="mb-1">
              {{ idx + 1 }}:
              <RouterLink :to="`/products/${p.id}`">
                ({{ p.type_label }}) {{ p.kor_co_nm }} - {{ p.fin_prdt_nm }}
              </RouterLink>
            </div>
          </div>

          <div class="fw-bold mb-2" v-if="joinedProducts.length > 0">
            가입한 상품 금리
          </div>

          <!-- ✅ 한 페이지(한 줄) 최대 4개씩 보여주기 -->
          <div v-if="joinedProducts.length > 0" class="d-flex justify-content-between align-items-center mb-2">
            <div class="text-muted small">
              {{ currentPage + 1 }} / {{ totalPages }} 페이지 (한 페이지당 {{ pageSize }}개)
            </div>
            <div class="d-flex gap-2">
              <button class="btn btn-outline-secondary btn-sm" :disabled="currentPage === 0" @click="prevPage">
                이전
              </button>
              <button class="btn btn-outline-secondary btn-sm" :disabled="currentPage >= totalPages - 1" @click="nextPage">
                다음
              </button>
            </div>
          </div>

          <!-- ✅ canvas는 DOM에서 제거하지 않음 (ref null 방지) -->
          <div class="border rounded p-3 bg-white chart-wrap" v-show="joinedProducts.length > 0">
            <canvas ref="chartCanvas" class="chart-canvas"></canvas>
          </div>
        </div>
      </template>

      <template v-else-if="tab === 'portfolio'">
        <h5 class="fw-bold">포트폴리오 수정</h5>
        <p class="text-muted mb-0">나중에 붙일 예정</p>
      </template>

      <template v-else-if="tab === 'recommend'">
        <h5 class="fw-bold">상품 추천 받기</h5>
        <p class="text-muted">나중에 붙일 예정</p>
        <button class="btn btn-primary" @click="doRecommend">추천 받기</button>

        <div v-if="result" class="alert alert-success mt-3 mb-0">
          추천 결과: <b>{{ result }}</b>
        </div>
      </template>

      <template v-else-if="tab === 'videos'">
        <h5 class="fw-bold">관심 동영상</h5>
        <p class="text-muted mb-3">저장한 관심 동영상 목록</p>

        <div v-if="videos.length === 0" class="text-muted">
          아직 저장된 동영상이 없습니다.
        </div>

        <ul v-else class="list-group">
          <li v-for="v in videos" :key="v.id" class="list-group-item">
            <div class="d-flex gap-3 align-items-start">
              <a :href="v.url" target="_blank" rel="noopener">
                <img
                  :src="getThumb(v)"
                  :alt="v.title"
                  style="width: 160px; height: 90px; object-fit: cover; border-radius: 8px;"
                />
              </a>

              <div class="flex-grow-1">
                <div class="fw-semibold mb-1">{{ v.title }}</div>
                <div v-if="v.channelTitle" class="text-muted small">채널명: {{ v.channelTitle }}</div>
                <div v-if="v.publishedAt" class="text-muted small mb-2">업로드 날짜: {{ v.publishedAt }}</div>
                <a :href="v.url" target="_blank" rel="noopener" class="small">
                  {{ v.url }}
                </a>
              </div>

              <button class="btn btn-outline-danger btn-sm" @click="removeVideo(v.id)">
                삭제
              </button>
            </div>
          </li>
        </ul>
      </template>
    </div>
  </main>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, onBeforeUnmount } from "vue"
import { useAuthStore } from "@/stores/auth"
import { useSavedVideosStore } from "@/stores/savedVideos"
import http from "@/api/http"
import { fetchProductDetail } from "@/api/products"
import Chart from "chart.js/auto"

const auth = useAuthStore()
const tab = ref("info")

const profile = ref({
  id: null,
  username: "",
  email: "",
  nickname: "",
  age: null,
  total_assets: null,
  income: null,
  joined_products: [],
})

const loading = ref(false)
const savingField = ref(null)
const errorMsg = ref("")
const successMsg = ref("")

const joinedProducts = ref([])
const joinedProductsLoading = ref(false)
const joinedErrorMsg = ref("")

const chartCanvas = ref(null)
let chartInstance = null

// ✅ (추가) 한 페이지에 최대 4개만 표시
const pageSize = 4
const currentPage = ref(0)

const totalPages = computed(() => {
  return Math.max(1, Math.ceil(joinedProducts.value.length / pageSize))
})

const pagedProducts = computed(() => {
  const start = currentPage.value * pageSize
  return joinedProducts.value.slice(start, start + pageSize)
})

function prevPage() {
  if (currentPage.value > 0) {
    currentPage.value -= 1
    drawChart()
  }
}

function nextPage() {
  if (currentPage.value < totalPages.value - 1) {
    currentPage.value += 1
    drawChart()
  }
}

// ✅ 차트 강제 리사이즈/업데이트 (초기 진입 “안 뜸” 방지)
function forceChartUpdate() {
  if (!chartInstance) return
  requestAnimationFrame(() => {
    try {
      chartInstance.resize()
      chartInstance.update()
    } catch (e) {
      // ignore
    }
  })
}

async function switchTab(next) {
  tab.value = next

  if (next === "info") {
    await drawChart()
  } else {
    destroyChart()
  }
}

function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms))
}

async function loadProfile() {
  loading.value = true
  errorMsg.value = ""
  successMsg.value = ""

  const MAX_TRY = 3

  for (let attempt = 1; attempt <= MAX_TRY; attempt++) {
    try {
      const res = await http.get("/api/accounts/profile/")
      profile.value = res.data
      await loadJoinedProducts()
      loading.value = false
      return
    } catch (err) {
      const status = err?.response?.status
      if ((status === 401 || status === 403) && attempt < MAX_TRY) {
        await sleep(150)
        continue
      }

      const detail = err?.response?.data?.detail
      errorMsg.value = detail || "프로필 정보를 불러오지 못했습니다."
      profile.value = {
        id: null,
        username: "",
        email: "",
        nickname: "",
        age: null,
        total_assets: null,
        income: null,
        joined_products: [],
      }
      joinedProducts.value = []
      destroyChart()
      loading.value = false
      return
    }
  }
}

async function onSaveField(field) {
  if (savingField.value !== null) return

  savingField.value = field
  errorMsg.value = ""
  successMsg.value = ""

  try {
    const payload = { [field]: profile.value[field] }
    const res = await http.patch("/api/accounts/profile/", payload)
    profile.value = res.data
    successMsg.value = "수정이 완료되었습니다."
    await loadJoinedProducts()
  } catch (err) {
    const data = err?.response?.data
    const detail = data?.detail
    const fieldMsg = Array.isArray(data?.[field]) ? data[field][0] : null
    errorMsg.value = detail || fieldMsg || "수정에 실패했습니다."
  } finally {
    savingField.value = null
  }
}

function normalizeJoinedIds(raw) {
  if (!Array.isArray(raw)) return []
  return raw
    .map((x) => {
      if (x == null) return null
      if (typeof x === "number") return x
      if (typeof x === "string") return Number(x)
      if (typeof x === "object" && x.id != null) return Number(x.id)
      return null
    })
    .filter((v) => Number.isFinite(v))
}

function destroyChart() {
  if (chartInstance) {
    chartInstance.destroy()
    chartInstance = null
  }
}

async function drawChart() {
  if (tab.value !== "info") return
  if (pagedProducts.value.length === 0) return

  await nextTick()
  await new Promise((r) => requestAnimationFrame(r))

  if (!chartCanvas.value) return

  const rect = chartCanvas.value.getBoundingClientRect()
  if (rect.width === 0 || rect.height === 0) {
    await new Promise((r) => requestAnimationFrame(r))
  }

  destroyChart()

  // ✅ 항상 4칸 고정: 1~3개인 페이지도 4개일 때와 동일한 폭/배치 유지
  const FIXED_SLOTS = pageSize // 4
  const slotLabels = Array(FIXED_SLOTS).fill("")
  const baseData = Array(FIXED_SLOTS).fill(null)
  const maxData = Array(FIXED_SLOTS).fill(null)

  pagedProducts.value.forEach((p, i) => {
    slotLabels[i] = p.fin_prdt_nm || `상품 ${p.id}`
    baseData[i] = p.baseRate ?? 0
    maxData[i] = p.maxRate ?? 0
  })

  const ctx = chartCanvas.value.getContext("2d")
  chartInstance = new Chart(ctx, {
    type: "bar",
    data: {
      labels: slotLabels,
      datasets: [
        { label: "기본 금리", data: baseData },
        { label: "최고 우대금리", data: maxData },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { position: "top" } },
      scales: {
        y: { beginAtZero: true },
        x: { offset: true }, // ✅ 슬롯(칸) 고정 느낌 강화
      },
    },
  })

  forceChartUpdate()
  requestAnimationFrame(forceChartUpdate)
}

async function loadJoinedProducts() {
  joinedProductsLoading.value = true
  joinedErrorMsg.value = ""
  joinedProducts.value = []
  destroyChart()

  try {
    const ids = normalizeJoinedIds(profile.value?.joined_products)

    if (ids.length === 0) {
      joinedProductsLoading.value = false
      await nextTick()
      destroyChart()
      return
    }

    const details = await Promise.all(
      ids.map(async (id) => {
        const d = await fetchProductDetail(id)

        const opts = Array.isArray(d?.options) ? d.options : []
        const baseRates = opts.map((o) => Number(o?.intr_rate)).filter((v) => !Number.isNaN(v))
        const maxRates = opts.map((o) => Number(o?.intr_rate2)).filter((v) => !Number.isNaN(v))

        const baseRate = baseRates.length ? Math.max(...baseRates) : 0
        const maxRate = maxRates.length ? Math.max(...maxRates) : 0

        return {
          id: d?.id,
          kor_co_nm: d?.kor_co_nm,
          fin_prdt_nm: d?.fin_prdt_nm,
          product_type: d?.product_type,
          type_label:
            d?.product_type === "DEPOSIT"
              ? "정기예금"
              : d?.product_type === "SAVING"
              ? "정기적금"
              : "상품",
          baseRate,
          maxRate,
        }
      })
    )

    joinedProducts.value = details

    // ✅ 가입 목록이 바뀌면 1페이지로 초기화
    currentPage.value = 0

    joinedProductsLoading.value = false
    await drawChart()
  } catch (e) {
    console.error(e)
    joinedErrorMsg.value = "가입한 상품 정보를 불러오지 못했습니다."
    joinedProducts.value = []
    joinedProductsLoading.value = false
    await nextTick()
    destroyChart()
  }
}

function handleResize() {
  forceChartUpdate()
}

onMounted(async () => {
  window.addEventListener("resize", handleResize)
  await loadProfile()

  if (tab.value === "info" && joinedProducts.value.length > 0) {
    await nextTick()
    requestAnimationFrame(() => {
      drawChart()
    })
  }
})

onBeforeUnmount(() => {
  window.removeEventListener("resize", handleResize)
  destroyChart()
})

// videos 탭 관련(기존 유지)
const result = ref("")
const savedStore = useSavedVideosStore()
const videos = computed(() => savedStore.list)

function removeVideo(id) {
  savedStore.remove(id)
}

function getThumb(v) {
  if (v.thumbnail) return v.thumbnail
  return `https://i.ytimg.com/vi/${v.id}/hqdefault.jpg`
}

function doRecommend() {
  result.value = "나중에 알고리즘 적용"
}
</script>

<style scoped>
.chart-wrap {
  height: 320px;
}
.chart-canvas {
  display: block;
  width: 100% !important;
  height: 100% !important;
}
</style>
