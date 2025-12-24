<template>
  <main class="container my-4">
    <div v-if="loading" class="text-center my-5">불러오는 중...</div>
    <div v-else-if="error" class="alert alert-danger">{{ error }}</div>

    <div v-else class="loan-card">
      <div class="filters">
        <div class="row g-2 align-items-end">
          <div class="col-12 col-md-4">
            <label class="form-label small mb-1">대출 종류</label>
            <div class="btn-group w-100" role="group">
              <button
                type="button"
                class="btn btn-sm"
                :class="loanCategory === 'mortgage' ? 'btn-primary' : 'btn-outline-primary'"
                @click="changeCategory('mortgage')"
              >
                주택담보대출
              </button>
              <button
                type="button"
                class="btn btn-sm"
                :class="loanCategory === 'renthouse' ? 'btn-primary' : 'btn-outline-primary'"
                @click="changeCategory('renthouse')"
              >
                전세자금대출
              </button>
            </div>
          </div>

          <div class="col-12 col-md-2">
            <label class="form-label small mb-1">은행</label>
            <select v-model="bank" class="form-select form-select-sm">
              <option value="전체">전체</option>
              <option v-for="b in banks" :key="b" :value="b">{{ b }}</option>
            </select>
          </div>

          <div class="col-12 col-md-2">
            <label class="form-label small mb-1">금리 기준</label>
            <select v-model="prdtType" class="form-select form-select-sm">
              <option value="all">전체</option>
              <option value="고정">고정금리</option>
              <option value="변동">변동금리</option>
            </select>
          </div>

          <div class="col-12 col-md-2">
            <label class="form-label small mb-1">가입 방법</label>
            <select v-model="joinWayFilter" class="form-select form-select-sm">
              <option value="all">전체</option>
              <option value="online">비대면</option>
              <option value="offline">영업점</option>
            </select>
          </div>

          <div class="col-12 col-md-2">
            <label class="form-label small mb-1">상품명</label>
            <input
              v-model="q"
              class="form-control form-control-sm"
              placeholder="상품명을 입력"
            />
          </div>

          <div class="col-12 d-flex flex-wrap gap-2 align-items-center mt-1">
            <div class="text-muted small">
              총 <span class="fw-bold">{{ filteredAndSorted.length }}</span>건
            </div>

            <div class="ms-auto d-flex flex-wrap gap-2 align-items-center">
              <select v-model="sortKey" class="form-select form-select-sm" style="width: 180px">
                <option value="MIN">최저금리</option>
                <option value="AVG">평균금리</option>
                <option value="MAX">최고금리</option>
                <option value="BANK">은행명</option>
                <option value="NAME">상품명</option>
              </select>

              <button class="btn btn-outline-secondary btn-sm" @click="toggleSortDir">
                {{ sortDir === "desc" ? "내림차순" : "오름차순" }}
              </button>
            </div>
          </div>
        </div>

        <div class="small text-muted mt-2">
          금리는 API 제공 값(lend_rate_min/avg/max)을 기준으로 표시합니다.
        </div>
      </div>

      <div class="table-responsive">
        <table class="table align-middle mb-0 loan-table">
          <thead>
            <tr>
              <th style="width: 160px">은행</th>
              <th>상품명</th>
              <th style="width: 120px">금리 기준</th>
              <th class="text-end" style="width: 110px">최저 금리</th>
              <th class="text-end" style="width: 110px">평균 금리</th>
              <th class="text-end" style="width: 110px">최고 금리</th>
              <th style="width: 120px">가입 방법</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="p in pagedItems"
              :key="p.fin_prdt_cd"
              class="row-click"
              @click="goDetail(p.fin_prdt_cd)"
            >
              <td class="fw-semibold">{{ p.kor_co_nm }}</td>
              <td class="product-name">{{ p.fin_prdt_nm }}</td>
              <td class="text-muted">{{ prdtTypeLabel(p.prdt_type) }}</td>
              <td class="text-end">
                <span :class="rateClass(p, 'min')">{{ rateText(p.lend_rate_min) }}</span>
              </td>
              <td class="text-end">
                <span :class="rateClass(p, 'avg')">{{ rateText(p.lend_rate_avg) }}</span>
              </td>
              <td class="text-end">
                <span :class="rateClass(p, 'max')">{{ rateText(p.lend_rate_max) }}</span>
              </td>
              <td class="text-muted">{{ joinWayLabel(p.join_way) }}</td>
            </tr>

            <tr v-if="filteredAndSorted.length === 0">
              <td colspan="7" class="text-center text-muted py-5">검색 결과가 없습니다.</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="pager">
        <button class="btn btn-outline-secondary btn-sm" :disabled="page === 1" @click="page--">
          이전
        </button>
        <div class="small text-muted">{{ page }} / {{ totalPages }}</div>
        <button
          class="btn btn-outline-secondary btn-sm"
          :disabled="page === totalPages"
          @click="page++"
        >
          다음
        </button>
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref, onMounted, computed, watch } from "vue"
import { useRouter } from "vue-router"
import { fetchLoans } from "@/api/loans"

const router = useRouter()

const loans = ref([])
const loading = ref(false)
const error = ref("")

const loanCategory = ref("mortgage")
const bank = ref("전체")
const prdtType = ref("all")
const joinWayFilter = ref("all")
const q = ref("")

const sortKey = ref("MIN")
const sortDir = ref("desc")

const page = ref(1)
const pageSize = ref(10)

const banks = computed(() => {
  const set = new Set()
  for (const p of loans.value || []) {
    if (p.kor_co_nm) set.add(p.kor_co_nm)
  }
  return Array.from(set).sort((a, b) => a.localeCompare(b))
})

function isOnlineJoin(joinWay) {
  const text = String(joinWay || "").toLowerCase()
  return ["인터넷", "모바일", "스마트", "online", "app", "비대면"].some((key) => text.includes(key))
}

function joinWayLabel(joinWay) {
  if (!joinWay) return "정보 없음"
  return isOnlineJoin(joinWay) ? "비대면" : "영업점"
}

function prdtTypeLabel(raw) {
  if (!raw) return "-"
  if (raw.includes("고정") && raw.includes("변동")) return "고정/변동"
  if (raw.includes("고정")) return "고정금리"
  if (raw.includes("변동")) return "변동금리"
  return raw
}

function rateText(value) {
  if (value === null || value === undefined || value === "") return "-"
  if (typeof value === "string" && value.trim() === "-") return "-"
  const num = Number(value)
  return Number.isFinite(num) ? `${num.toFixed(2)}%` : "-"
}

function rateValue(value) {
  if (value === null || value === undefined || value === "") return -Infinity
  if (typeof value === "string" && value.trim() === "-") return -Infinity
  const num = Number(value)
  return Number.isFinite(num) ? num : -Infinity
}

function rateClass(product, key) {
  const values = [
    rateValue(product.lend_rate_min),
    rateValue(product.lend_rate_avg),
    rateValue(product.lend_rate_max),
  ].filter((v) => Number.isFinite(v))
  if (values.length === 0) return "rate-missing"

  const selected =
    key === "min"
      ? rateValue(product.lend_rate_min)
      : key === "avg"
      ? rateValue(product.lend_rate_avg)
      : rateValue(product.lend_rate_max)

  const maxRate = Math.max(...values)
  return selected === maxRate ? "rate-max" : "rate-base"
}

async function fetchLoanList() {
  loading.value = true
  error.value = ""
  page.value = 1

  try {
    const data = await fetchLoans({ category: loanCategory.value })
    loans.value = data || []
  } catch (e) {
    error.value = "대출 상품을 불러오지 못했습니다."
  } finally {
    loading.value = false
  }
}

async function changeCategory(category) {
  if (loanCategory.value === category) return
  loanCategory.value = category
  bank.value = "전체"
  prdtType.value = "all"
  joinWayFilter.value = "all"
  q.value = ""
  await fetchLoanList()
}

const filteredAndSorted = computed(() => {
  let list = [...(loans.value || [])]

  if (bank.value !== "전체") {
    list = list.filter((p) => p.kor_co_nm === bank.value)
  }

  if (q.value) {
    const needle = q.value.toLowerCase()
    list = list.filter((p) => String(p.fin_prdt_nm || "").toLowerCase().includes(needle))
  }

  if (prdtType.value !== "all") {
    list = list.filter((p) => String(p.prdt_type || "").includes(prdtType.value))
  }

  if (joinWayFilter.value === "online") {
    list = list.filter((p) => isOnlineJoin(p.join_way))
  } else if (joinWayFilter.value === "offline") {
    list = list.filter((p) => p.join_way && !isOnlineJoin(p.join_way))
  }

  const dir = sortDir.value === "desc" ? -1 : 1
  list.sort((a, b) => {
    if (sortKey.value === "BANK") {
      return String(a.kor_co_nm || "").localeCompare(String(b.kor_co_nm || "")) * dir
    }
    if (sortKey.value === "NAME") {
      return String(a.fin_prdt_nm || "").localeCompare(String(b.fin_prdt_nm || "")) * dir
    }
    const key =
      sortKey.value === "AVG"
        ? "lend_rate_avg"
        : sortKey.value === "MAX"
        ? "lend_rate_max"
        : "lend_rate_min"
    return (rateValue(b[key]) - rateValue(a[key])) * dir
  })

  return list
})

const totalPages = computed(() =>
  Math.max(1, Math.ceil(filteredAndSorted.value.length / pageSize.value))
)

const pagedItems = computed(() => {
  const start = (page.value - 1) * pageSize.value
  return filteredAndSorted.value.slice(start, start + pageSize.value)
})

watch([bank, prdtType, joinWayFilter, q, sortKey, sortDir], () => {
  page.value = 1
})

function toggleSortDir() {
  sortDir.value = sortDir.value === "desc" ? "asc" : "desc"
}

function goDetail(finPrdtCd) {
  router.push({
    path: `/loans/${finPrdtCd}`,
    query: { category: loanCategory.value },
  })
}

onMounted(async () => {
  await fetchLoanList()
})
</script>

<style scoped>
.loan-card {
  background: #fff;
  border: 1px solid #e9ecef;
  border-radius: 14px;
  padding: 18px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06);
}

.filters {
  padding-bottom: 14px;
  margin-bottom: 8px;
  border-bottom: 1px solid #eef1f4;
}

.loan-table thead th {
  background: #f8f9fa;
  font-weight: 800;
  font-size: 0.92rem;
  border-bottom: 1px solid #e9ecef;
  white-space: nowrap;
}

.loan-table tbody td {
  border-bottom: 1px solid #f1f3f5;
}

.row-click {
  cursor: pointer;
}

.row-click:hover {
  background: #fbfcfd;
}

.product-name {
  word-break: keep-all;
}

.rate-base {
  color: #000;
  font-weight: 400;
}

.rate-max {
  color: #000;
  font-weight: 700;
}

.rate-missing {
  color: #adb5bd;
  font-weight: 400;
}

.pager {
  margin-top: 16px;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 14px;
}
</style>
