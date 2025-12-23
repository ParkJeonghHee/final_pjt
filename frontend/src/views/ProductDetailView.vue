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
              {{ product.kor_co_nm }} ·
              {{ product.product_type === "DEPOSIT" ? "정기예금" : "정기적금" }}
            </div>
          </div>

          <div>
            <button
              v-if="product.is_joined"
              class="btn btn-secondary px-4 py-2 rounded-3"
              disabled
            >
              가입 완료
            </button>

            <button
              v-else-if="isLoggedIn"
              class="btn btn-primary px-4 py-2 rounded-3"
              @click="joinProduct"
            >
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
        <h5 class="fw-bold mb-3">금리 옵션</h5>
        <div class="table-responsive">
          <table class="table align-middle mb-0">
            <thead class="table-light">
              <tr>
                <th style="width: 18%">기간</th>
                <th style="width: 22%">기본금리</th>
                <th style="width: 22%">우대금리(최고)</th>
                <th style="width: 38%">금리유형</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="o in (product.options || [])" :key="o.id">
                <td>{{ o.save_trm }}개월</td>
                <td class="text-primary fw-medium">{{ formatRate(o.intr_rate) }}</td>
                <td class="text-danger fw-bold">{{ formatRate(o.intr_rate2) }}</td>
                <td>
                  <span class="badge rounded-3 px-3 py-2 rate-badge">
                    {{ o.intr_rate_type_nm }}
                  </span>
                </td>
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
          <div class="fw-bold mb-2">우대금리 조건</div>
          <ul class="mb-0 ps-3">
            <li v-for="(line, idx) in preferRateGuide" :key="idx">{{ line }}</li>
          </ul>
        </div>
      </section>

      <section v-else-if="activeTab === 'join'" class="card shadow-sm border-0 p-4 rounded-4">
        <h5 class="fw-bold mb-3">가입대상 및 조건</h5>
        <ul v-if="joinInfoLines.length" class="text-muted mb-0 ps-3">
          <li v-for="(line, idx) in joinInfoLines" :key="idx">{{ line }}</li>
        </ul>
        <div v-else class="text-muted">가입조건 정보가 없습니다.</div>
      </section>

      <section v-else-if="activeTab === 'feature'" class="card shadow-sm border-0 p-4 rounded-4">
        <h5 class="fw-bold mb-3">상품특징</h5>
        <div class="text-muted" style="white-space: pre-line;">
          {{ featureInfoText }}
        </div>
      </section>

      <section v-else class="card shadow-sm border-0 p-4 rounded-4">
        <h5 class="fw-bold mb-3">상세정보</h5>
        <div class="mb-0">
          <div class="fw-semibold mb-1">가입 방법</div>
          <div class="text-muted" style="white-space: pre-line;">
            {{ detailInfoText }}
          </div>
        </div>
      </section>

      <div class="warn-box mt-4">
        <div class="fw-bold mb-2">⚠️ 금융소비자 보호 안내</div>
        <div class="mb-0 small">
          본 상품은 예금자보호법에 따라 예금보험공사가 보호하며, 보호 한도는
          1인당 “최고 5천만원”입니다. (이자 포함)
        </div>
      </div>
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
  { key: "rate", label: "금리 옵션" },
  { key: "join", label: "가입조건" },
  { key: "feature", label: "상품특징" },
  { key: "detail", label: "상세정보" },
]

const activeTab = ref("rate")

const isLoggedIn = computed(() => !!localStorage.getItem("access")) // 토큰 키값 확인 필요

/**
 * ✅ 우대금리 안내 (spcl_cnd 필드 사용 권장)
 * DB나 API에서 넘어오는 필드명이 'spcl_cnd'일 가능성이 높습니다.
 */
const preferRateGuide = computed(() => {
  const v = product.value?.spcl_cnd || product.value?.prefer_rate_guide

  if (Array.isArray(v) && v.length) return v
  if (typeof v === "string" && v.trim()) return v.split("\n").filter(Boolean)

  return [
    "급여/연금 이체 실적(월 1회 이상)",
    "자동이체 2건 이상 등록",
    "모바일/인터넷뱅킹 가입 및 로그인",
    "신규 고객/첫 거래 우대",
    "카드 실적 또는 특정 이벤트 참여",
  ]
})

const joinInfoLines = computed(() => {
  const join = normalizeLines(product.value?.join_member)
  const deny = normalizeLines(product.value?.join_deny)
  return [...join, ...deny].filter(Boolean)
})

const featureInfoText = computed(() => {
  const v = normalizeText(product.value?.etc_note)
  if (v) return v

  return [
    "최소 가입금액 및 만기 조건은 상품별 상이",
    "만기 자동해지 또는 자동재예치 선택 가능",
    "금리 변동 시 적용 시점은 상품 안내 기준",
    "세부 혜택은 이벤트 및 은행 정책에 따라 달라짐",
  ].join("\n")
})

const detailInfoText = computed(() => {
  const v = normalizeText(product.value?.join_way)
  if (v) return v

  return [
    "가입 채널: 영업점, 인터넷뱅킹, 모바일앱",
    "서류: 신분증 및 본인확인 수단",
    "유의사항: 중도해지 시 금리 하락 가능",
    "세부 조건은 상품 안내서를 참고",
  ].join("\n")
})

function normalizeText(v) {
  if (v === null || v === undefined) return ""
  const s = String(v).trim()
  return s ? s : ""
}

function normalizeLines(v) {
  const s = normalizeText(v)
  if (!s) return []
  return s
    .split(/[\n;•·]/g)
    .map((line) => line.trim())
    .filter(Boolean)
}

/**
 * 🔹 금리 포맷팅 함수
 * 값이 없으면 '-', 있으면 소수점 2자리까지 표시 (예: 2.4 -> 2.40)
 */
function formatRate(value) {
  if (value === null || value === undefined || value === "") return "-"
  const num = Number(value)
  return isNaN(num) ? value : num.toFixed(2) + "%"
}

function safeText(v, fallback) {
  if (v === null || v === undefined) return fallback
  const s = String(v).trim()
  return s ? s : fallback
}

onMounted(async () => {
  try {
    const id = route.params.id
    const res = await http.get(`/api/products/${id}/`)
    product.value = res.data
  } catch (e) {
    console.error(e)
    error.value = "상품 정보를 불러오는데 실패했습니다."
  } finally {
    loading.value = false
  }
})

async function joinProduct() {
  if (!confirm("이 상품에 가입하시겠습니까?")) return

  try {
    const id = route.params.id
    // 필요 시 post body에 데이터 추가 (예: 가입 기간 등)
    await http.post(`/api/products/${id}/join/`)
    
    // UI 즉시 반영
    if (product.value) {
      product.value = { ...product.value, is_joined: true }
    }
    alert("성공적으로 가입되었습니다.")
  } catch (e) {
    console.error(e)
    alert("가입 처리에 실패했습니다. 이미 가입된 상품인지 확인해주세요.")
  }
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

.info-box {
  background: #f3f0ff; /* 연한 보라빛 배경 변경 (가독성) */
  color: #5f3dc4;
  border-radius: 12px;
  padding: 20px;
}

.warn-box {
  background: #fff9db;
  border: 1px solid #ffec99;
  color: #e67700;
  border-radius: 12px;
  padding: 16px;
}
</style>
