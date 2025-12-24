<template>
  <main class="container my-4">
    <div v-if="loading" class="text-center py-5">불러오는 중...</div>
    <div v-else-if="error" class="alert alert-danger">{{ error }}</div>

    <div v-else-if="product">
      <div class="card shadow-sm border-0 p-4 mb-3 rounded-4">
        <div class="d-flex justify-content-between align-items-center">
          <div>
            <h3 class="fw-bold mb-1">{{ product.fin_prdt_nm }}</h3>
            <div class="text-muted">
              {{ product.kor_co_nm }} · {{ categoryLabel }}
            </div>
          </div>

          <div>
            <button v-if="isJoined" class="btn btn-secondary px-4 py-2 rounded-3" disabled>
              가입 완료
            </button>

            <button v-else-if="isLoggedIn" class="btn btn-primary px-4 py-2 rounded-3" @click="confirmJoin">
              가입하기
            </button>

            <div v-else class="text-end">
              <span class="badge bg-light text-dark border">로그인 필요</span>
            </div>
          </div>
        </div>
      </div>

      <div class="tabs-wrap mb-3">
        <button
          v-for="t in tabs"
          :key="t.key"
          type="button"
          class="tab-btn"
          :class="{ active: activeTab === t.key }"
          @click="activeTab = t.key"
        >
          {{ t.label }}
        </button>
      </div>

      <section v-if="activeTab === 'rate'" class="card shadow-sm border-0 p-4 rounded-4">
        <h5 class="fw-bold mb-3">금리 정보</h5>
        <div class="row g-3 mb-3">
          <div class="col-12 col-md-4">
            <div class="summary-box">
              <div class="text-muted small">최저 금리</div>
              <div class="fw-bold">{{ formatRate(summaryRates.min) }}</div>
            </div>
          </div>
          <div class="col-12 col-md-4">
            <div class="summary-box">
              <div class="text-muted small">평균 금리</div>
              <div class="fw-bold">{{ formatRate(summaryRates.avg) }}</div>
            </div>
          </div>
          <div class="col-12 col-md-4">
            <div class="summary-box">
              <div class="text-muted small">최고 금리</div>
              <div class="fw-bold">{{ formatRate(summaryRates.max) }}</div>
            </div>
          </div>
        </div>

        <div class="table-responsive">
          <table class="table align-middle mb-0">
            <thead class="table-light">
              <tr>
                <th style="width: 30%">금리 기준</th>
                <th class="text-end" style="width: 23%">최저 금리</th>
                <th class="text-end" style="width: 23%">평균 금리</th>
                <th class="text-end" style="width: 24%">최고 금리</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(o, idx) in (product.options || [])" :key="idx">
                <td>
                  <span class="badge rounded-3 px-3 py-2 rate-badge">
                    {{ optionRateType(o) }}
                  </span>
                </td>
                <td class="text-end">{{ formatRate(o.lend_rate_min) }}</td>
                <td class="text-end">{{ formatRate(o.lend_rate_avg) }}</td>
                <td class="text-end">{{ formatRate(o.lend_rate_max) }}</td>
              </tr>
              <tr v-if="!product.options || product.options.length === 0">
                <td colspan="4" class="text-muted py-4 text-center">
                  금리 옵션 정보가 없습니다.
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="info-box mt-4">
          <div class="fw-bold mb-2">대출 금리 안내</div>
          <ul class="mb-0 ps-3">
            <li>상품 타입(prdt_type)에 따라 고정/변동 금리가 다를 수 있습니다.</li>
            <li>최저·평균·최고 금리는 조건에 따라 달라질 수 있습니다.</li>
            <li>비대면/영업점 가입 여부는 join_way를 참고하세요.</li>
          </ul>
        </div>
      </section>

      <section v-else-if="activeTab === 'join'" class="card shadow-sm border-0 p-4 rounded-4">
        <h5 class="fw-bold mb-3">가입 방법</h5>
        <div class="text-muted" style="white-space: pre-line;">
          {{ joinWayText }}
        </div>
      </section>

      <section v-else class="card shadow-sm border-0 p-4 rounded-4">
        <h5 class="fw-bold mb-3">상세정보</h5>
        <div class="mb-0">
          <div class="fw-semibold mb-1">상품 코드</div>
          <div class="text-muted">{{ product.fin_prdt_cd }}</div>
        </div>
        <div class="mb-0 mt-3">
          <div class="fw-semibold mb-1">금리 기준</div>
          <div class="text-muted">{{ prdtTypeText }}</div>
        </div>
      </section>
    </div>
  </main>
</template>

<script setup>
import { ref, onMounted, computed } from "vue"
import { useRoute } from "vue-router"
import http from "@/api/http"

const route = useRoute()
const product = ref(null)
const loading = ref(true)
const error = ref("")

const tabs = [
  { key: "rate", label: "금리 정보" },
  { key: "join", label: "가입 방법" },
  { key: "detail", label: "상세정보" },
]

const activeTab = ref("rate")
const isJoined = ref(false)
const isLoggedIn = computed(() => !!localStorage.getItem("access"))

const joinedStorageKey = "loan_joined"

const categoryLabel = computed(() => {
  const category = String(route.query.category || "mortgage")
  if (category === "mortgage") return "주택담보대출"
  if (category === "renthouse") return "전세자금대출"
  return "주택담보대출"
})

const joinWayText = computed(() => {
  return normalizeText(product.value?.join_way) || "가입 방법 정보가 없습니다."
})

const prdtTypeText = computed(() => {
  const v = normalizeText(product.value?.prdt_type)
  return v || "금리 기준 정보가 없습니다."
})

const summaryRates = computed(() => {
  const fromProduct = {
    min: product.value?.lend_rate_min,
    avg: product.value?.lend_rate_avg,
    max: product.value?.lend_rate_max,
  }

  const hasAny =
    isFiniteRate(fromProduct.min) || isFiniteRate(fromProduct.avg) || isFiniteRate(fromProduct.max)
  if (hasAny) return fromProduct

  const options = Array.isArray(product.value?.options) ? product.value.options : []
  const mins = []
  const maxs = []
  const avgs = []

  for (const opt of options) {
    const minVal = parseRate(opt?.lend_rate_min)
    const maxVal = parseRate(opt?.lend_rate_max)
    const avgVal = parseRate(opt?.lend_rate_avg)
    if (minVal !== null) mins.push(minVal)
    if (maxVal !== null) maxs.push(maxVal)
    if (avgVal !== null) avgs.push(avgVal)
  }

  return {
    min: mins.length ? Math.min(...mins) : null,
    avg: avgs.length ? avgs.reduce((sum, v) => sum + v, 0) / avgs.length : null,
    max: maxs.length ? Math.max(...maxs) : null,
  }
})

function optionRateType(option) {
  return option?.prdt_type_nm || option?.prdt_type || option?.lend_rate_type_nm || "기타"
}

function normalizeText(v) {
  if (v === null || v === undefined) return ""
  const s = String(v).trim()
  return s ? s : ""
}

function parseRate(value) {
  if (value === null || value === undefined || value === "") return null
  if (typeof value === "string" && value.trim() === "-") return null
  const num = Number(value)
  return Number.isFinite(num) ? num : null
}

function isFiniteRate(value) {
  return parseRate(value) !== null
}

function formatRate(value) {
  if (value === null || value === undefined || value === "") return "-"
  const num = Number(value)
  return Number.isFinite(num) ? `${num.toFixed(2)}%` : "-"
}

onMounted(async () => {
  try {
    const finPrdtCd = route.params.finPrdtCd
    const category = route.query.category || "mortgage"
    const res = await http.get(`/api/loans/${finPrdtCd}/`, { params: { category } })
    product.value = res.data
    isJoined.value = hasJoined(res.data?.fin_prdt_cd)
  } catch (e) {
    console.error(e)
    error.value = "대출 상품 정보를 불러오는데 실패했습니다."
  } finally {
    loading.value = false
  }
})

function hasJoined(finPrdtCd) {
  const list = loadJoined()
  return finPrdtCd ? list.some((item) => item.fin_prdt_cd === finPrdtCd) : false
}

function loadJoined() {
  try {
    const raw = localStorage.getItem(joinedStorageKey)
    const parsed = raw ? JSON.parse(raw) : []
    if (!Array.isArray(parsed)) return []

    const normalized = parsed
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
      .filter((v) => v && v.fin_prdt_cd && v.category !== "credit")

    localStorage.setItem(joinedStorageKey, JSON.stringify(normalized))
    return normalized
  } catch (e) {
    return []
  }
}

function saveJoined(list) {
  localStorage.setItem(joinedStorageKey, JSON.stringify(list))
}

function confirmJoin() {
  if (!product.value?.fin_prdt_cd) return
  if (!confirm("해당 대출상품 가입을 확인하시겠습니까?")) return
  const list = loadJoined()
  const exists = list.some((item) => item.fin_prdt_cd === product.value.fin_prdt_cd)
  if (!exists) {
    list.push({
      fin_prdt_cd: product.value.fin_prdt_cd,
      category: route.query.category || "mortgage",
      kor_co_nm: product.value.kor_co_nm,
      fin_prdt_nm: product.value.fin_prdt_nm,
    })
  }
  saveJoined(list)
  isJoined.value = true
}
</script>

<style scoped>
.tabs-wrap {
  display: flex;
  gap: 8px;
  padding: 8px;
  background: #f8f9fa;
  border-radius: 16px;
  overflow-x: auto;
  white-space: nowrap;
}

.tab-btn {
  border: 0;
  background: transparent;
  padding: 10px 20px;
  border-radius: 12px;
  font-weight: 600;
  color: #868e96;
  transition: all 0.2s ease;
}

.tab-btn.active {
  background: #ffffff;
  color: #212529;
  box-shadow: 0 2px 6px rgba(0,0,0,0.06);
}

.rate-badge {
  background: #e7f5ff;
  color: #0c8599;
  font-weight: 700;
  font-size: 0.85rem;
}

.summary-box {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 12px;
  padding: 14px 16px;
}

.info-box {
  background: #f3f0ff;
  color: #5f3dc4;
  border-radius: 12px;
  padding: 20px;
}
</style>
