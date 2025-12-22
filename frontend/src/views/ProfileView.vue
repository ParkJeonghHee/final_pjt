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
              {{ savingField === 'email' ? "수정 중..." : "수정하기" }}
            </button>
          </div>

          <div class="mb-3 d-flex gap-2 align-items-end">
            <div class="flex-grow-1">
              <label class="form-label">Nickname</label>
              <input class="form-control" v-model="profile.nickname" placeholder="닉네임을 설정해주세요" />
            </div>
            <button class="btn btn-primary" :disabled="savingField !== null" @click="onSaveField('nickname')">
              {{ savingField === 'nickname' ? "수정 중..." : "수정하기" }}
            </button>
          </div>

          <div class="mb-3 d-flex gap-2 align-items-end">
            <div class="flex-grow-1">
              <label class="form-label">나이</label>
              <input class="form-control" v-model.number="profile.age" type="number" min="0" />
            </div>
            <button class="btn btn-primary" :disabled="savingField !== null" @click="onSaveField('age')">
              {{ savingField === 'age' ? "수정 중..." : "수정하기" }}
            </button>
          </div>

          <div class="mb-3 d-flex gap-2 align-items-end">
            <div class="flex-grow-1">
              <label class="form-label">총 자산</label>
              <input class="form-control" v-model.number="profile.total_assets" type="number" min="0" />
            </div>
            <button class="btn btn-primary" :disabled="savingField !== null" @click="onSaveField('total_assets')">
              {{ savingField === 'total_assets' ? "수정 중..." : "수정하기" }}
            </button>
          </div>

          <div class="mb-4 d-flex gap-2 align-items-end">
            <div class="flex-grow-1">
              <label class="form-label">월 소득</label>
              <input class="form-control" v-model.number="profile.income" type="number" min="0" />
            </div>
            <button class="btn btn-primary" :disabled="savingField !== null" @click="onSaveField('income')">
              {{ savingField === 'income' ? "수정 중..." : "수정하기" }}
            </button>
          </div>

          <hr class="my-4" />

          <h5 class="fw-bold mb-2">가입한 상품들</h5>

          <div v-if="joinedProductsLoading" class="text-muted mb-3">
            가입한 상품 불러오는 중...
          </div>

          <div v-else>
            <div v-if="joinedErrorMsg" class="text-danger fw-semibold mb-3">
              {{ joinedErrorMsg }}
            </div>

            <div v-if="joinedProducts.length === 0" class="text-muted mb-3">
              가입한 상품이 없습니다.
            </div>

            <div v-else>
              <div class="mb-3">
                <div v-for="(p, idx) in joinedProducts" :key="p.id" class="mb-1">
                  {{ idx + 1 }}:
                  <RouterLink :to="`/products/${p.id}`">
                    ({{ p.type_label }}) {{ p.kor_co_nm }} - {{ p.fin_prdt_nm }}
                  </RouterLink>
                </div>
              </div>

              <div class="fw-bold mb-2">가입한 상품 금리</div>
              <div class="border rounded p-3 bg-white" style="height: 320px;">
                <canvas ref="chartCanvas" style="width: 100%; height: 100%;"></canvas>
              </div>
            </div>
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
                <div v-if="v.channelTitle" class="text-muted small">
                  채널명: {{ v.channelTitle }}
                </div>
                <div v-if="v.publishedAt" class="text-muted small mb-2">
                  업로드 날짜: {{ v.publishedAt }}
                </div>
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
import { ref, computed, onMounted, nextTick } from "vue"
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

function switchTab(next) {
  tab.value = next
  if (next === "info") {
    nextTick(() => {
      if (joinedProducts.value.length > 0) drawChart()
    })
  } else {
    destroyChart()
  }
}

async function loadProfile() {
  loading.value = true
  errorMsg.value = ""
  successMsg.value = ""

  try {
    const res = await http.get("/api/accounts/profile/")
    profile.value = res.data
    await loadJoinedProducts()
  } catch (err) {
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
  } finally {
    loading.value = false
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

async function loadJoinedProducts() {
  joinedProductsLoading.value = true
  joinedErrorMsg.value = ""
  joinedProducts.value = []

  try {
    const ids = normalizeJoinedIds(profile.value?.joined_products)

    if (ids.length === 0) {
      destroyChart()
      return
    }

    const details = await Promise.all(
      ids.map(async (id) => {
        const d = await fetchProductDetail(id)

        let baseRate = 0
        let maxRate = 0

        if (Array.isArray(d.options) && d.options.length > 0) {
          const bases = d.options.map((o) => Number(o.intr_rate)).filter((v) => !Number.isNaN(v))
          const maxs = d.options.map((o) => Number(o.intr_rate2)).filter((v) => !Number.isNaN(v))
          baseRate = bases.length ? Math.max(...bases) : 0
          maxRate = maxs.length ? Math.max(...maxs) : 0
        } else {
          const b = Number(d.intr_rate)
          const m = Number(d.intr_rate2)
          baseRate = Number.isNaN(b) ? 0 : b
          maxRate = Number.isNaN(m) ? 0 : m
        }

        return {
          id: d.id,
          kor_co_nm: d.kor_co_nm,
          fin_prdt_nm: d.fin_prdt_nm,
          type: d.type,
          type_label: d.type === "DEPOSIT" ? "정기예금" : d.type === "SAVING" ? "정기적금" : "상품",
          baseRate,
          maxRate,
        }
      })
    )

    joinedProducts.value = details

    await nextTick()
    if (tab.value === "info") drawChart()
  } catch (e) {
    joinedErrorMsg.value = "가입한 상품 정보를 불러오지 못했습니다."
    joinedProducts.value = []
    destroyChart()
  } finally {
    joinedProductsLoading.value = false
  }
}

function destroyChart() {
  if (chartInstance) {
    chartInstance.destroy()
    chartInstance = null
  }
}

function drawChart() {
  if (!chartCanvas.value) return
  if (joinedProducts.value.length === 0) return

  destroyChart()

  const labels = joinedProducts.value.map((p) => p.fin_prdt_nm)
  const baseData = joinedProducts.value.map((p) => p.baseRate)
  const maxData = joinedProducts.value.map((p) => p.maxRate)

  chartInstance = new Chart(chartCanvas.value, {
    type: "bar",
    data: {
      labels,
      datasets: [
        { label: "기본 금리", data: baseData },
        { label: "최고 우대금리", data: maxData },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { position: "top" } },
      scales: { y: { beginAtZero: true } },
    },
  })
}

onMounted(() => {
  loadProfile()
})

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
