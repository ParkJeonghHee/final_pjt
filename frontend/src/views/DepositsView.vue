<template>
  <main class="container my-4 deposits-page">

    <!-- ✅ 2번 이미지 느낌: 심플한 타이틀 + 카드형 테이블 -->

    <div v-if="loading" class="text-center my-5">불러오는 중...</div>
    <div v-else-if="error" class="alert alert-danger">{{ error }}</div>

    <div v-else class="rate-card">
      <div class="filters">
        <div class="row g-2 align-items-end">
          <div class="col-12 col-md-3">
            <label class="form-label small mb-1">상품 타입</label>
            <div class="btn-group w-100" role="group">
              <button
                type="button"
                class="btn btn-sm"
                :class="productType === 'DEPOSIT' ? 'btn-primary' : 'btn-outline-primary'"
                @click="changeType('DEPOSIT')"
              >
                정기예금
              </button>
              <button
                type="button"
                class="btn btn-sm"
                :class="productType === 'SAVING' ? 'btn-primary' : 'btn-outline-primary'"
                @click="changeType('SAVING')"
              >
                정기적금
              </button>
            </div>
          </div>

          <div class="col-12 col-md-3">
            <label class="form-label small mb-1">은행</label>
            <select v-model="bank" class="form-select form-select-sm">
              <option value="전체">전체</option>
              <option v-for="b in banks" :key="b" :value="b">{{ b }}</option>
            </select>
          </div>

          <div class="col-12 col-md-2">
            <label class="form-label small mb-1">예치기간</label>
            <select v-model="term" class="form-select form-select-sm">
              <option value="">전체기간</option>
              <option value="6">6개월</option>
              <option value="12">12개월</option>
              <option value="24">24개월</option>
              <option value="36">36개월</option>
            </select>
          </div>

          <div class="col-12 col-md-4">
            <label class="form-label small mb-1">상품명</label>
            <input
              v-model="q"
              class="form-control form-control-sm"
              placeholder="상품명 검색"
              @keyup.enter="fetchProductsList"
            />
          </div>

          <div class="col-12 d-flex flex-wrap gap-2 align-items-center mt-1">
            <div class="form-check">
              <input
                class="form-check-input"
                type="checkbox"
                id="onlyWithTerm"
                v-model="onlyWithSelectedTerm"
                :disabled="!selectedMonths"
              />
              <label class="form-check-label small" for="onlyWithTerm">
                선택 기간 금리 있는 상품만
              </label>
            </div>

            <div class="ms-auto d-flex flex-wrap gap-2 align-items-center">
              <div class="text-muted small">
                총 <span class="fw-bold">{{ filteredAndSorted.length }}</span>건
              </div>

              <select v-model="sortKey" class="form-select form-select-sm" style="width: 180px">
                <option value="RATE_DESC">금리</option>
                <option value="BANK_ASC">은행명</option>
                <option value="NAME_ASC">상품명</option>
              </select>

              <button class="btn btn-outline-secondary btn-sm" @click="toggleSortDir">
                {{ sortDir === "desc" ? "내림차순" : "오름차순" }}
              </button>

              <button type="button" class="btn btn-secondary btn-sm" @click="fetchProductsList">
                조회
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="table-responsive">
        <table class="table align-middle mb-0 rate-table">
          <thead>
            <tr>
              <th style="width: 180px">금융회사명</th>
              <th>상품명</th>
              <th class="text-end" style="width: 110px">6개월</th>
              <th class="text-end" style="width: 110px">12개월</th>
              <th class="text-end" style="width: 110px">24개월</th>
              <th class="text-end" style="width: 110px">36개월</th>
            </tr>
          </thead>

          <tbody>
            <tr
              v-for="p in pagedItems"
              :key="p.id"
              class="row-click"
              @click="goDetail(p.id)"
            >
              <td class="fw-semibold">{{ p.kor_co_nm }}</td>
              <td class="product-name">{{ p.fin_prdt_nm }}</td>

              <td class="text-end">
                <span :class="rateClass(p, 6)">{{ rateText(p, 6) }}</span>
              </td>
              <td class="text-end">
                <span :class="rateClass(p, 12)">{{ rateText(p, 12) }}</span>
              </td>
              <td class="text-end">
                <span :class="rateClass(p, 24)">{{ rateText(p, 24) }}</span>
              </td>
              <td class="text-end">
                <span :class="rateClass(p, 36)">{{ rateText(p, 36) }}</span>
              </td>
            </tr>

            <tr v-if="filteredAndSorted.length === 0">
              <td colspan="6" class="text-center text-muted py-5">검색 결과가 없습니다.</td>
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
import { fetchProducts, fetchBanks, syncProducts } from "@/api/products"

const router = useRouter()

const products = ref([])
const banks = ref([])

const loading = ref(false)
const error = ref("")

const productType = ref("DEPOSIT") // DEPOSIT | SAVING
const bank = ref("전체")
const term = ref("")
const q = ref("")

const onlyWithSelectedTerm = ref(false)
const sortKey = ref("RATE_DESC") // RATE_DESC | BANK_ASC | NAME_ASC
const sortDir = ref("desc") // desc | asc

const page = ref(1)
const pageSize = ref(10)

const selectedMonths = computed(() => Number(term.value || 12))

async function ensureBanksLoaded() {
  let bankList = await fetchBanks(productType.value)
  const isEmpty =
    !bankList || bankList.length === 0 || (bankList.length === 1 && bankList[0] === "전체")

  if (isEmpty) {
    await syncProducts()
    bankList = await fetchBanks(productType.value)
  }

  banks.value = (bankList || []).filter((b) => b !== "전체")
}

async function fetchProductsList() {
  loading.value = true
  error.value = ""
  page.value = 1

  try {
    const data = await fetchProducts(productType.value, {
      bank: bank.value,
      term: term.value,
      q: q.value,
    })
    products.value = data
  } catch (e) {
    error.value = "상품 목록을 불러오지 못했습니다."
  } finally {
    loading.value = false
  }
}

async function changeType(type) {
  if (productType.value === type) return

  productType.value = type
  bank.value = "전체"
  term.value = ""
  q.value = ""
  onlyWithSelectedTerm.value = false

  loading.value = true
  error.value = ""

  try {
    await ensureBanksLoaded()
    await fetchProductsList()
  } catch (e) {
    error.value = "데이터를 불러오지 못했습니다."
  } finally {
    loading.value = false
  }
}

function goDetail(id) {
  router.push(`/products/${id}`)
}

function extractRates(p) {
  const flat = {
    6: p.rate_6 ?? p.intr_rate_6,
    12: p.rate_12 ?? p.intr_rate_12,
    24: p.rate_24 ?? p.intr_rate_24,
    36: p.rate_36 ?? p.intr_rate_36,
  }
  const hasAnyFlat = Object.values(flat).some((v) => v !== undefined && v !== null && v !== "")
  if (hasAnyFlat) return flat

  const arr =
    p.options ||
    p.depositoptions ||
    p.savingoptions ||
    p.deposit_options ||
    p.saving_options ||
    []

  const map = { 6: null, 12: null, 24: null, 36: null }

  for (const opt of arr) {
    const t = Number(opt.save_trm ?? opt.term ?? opt.trm ?? opt.month)
    if (![6, 12, 24, 36].includes(t)) continue

    const r = opt.intr_rate2 ?? opt.intr_rate ?? opt.rate ?? null
    if (r === null || r === undefined || r === "") continue

    const num = Number(r)
    if (Number.isFinite(num)) {
      map[t] = map[t] === null ? num : Math.max(map[t], num)
    }
  }

  return map
}

function rateText(p, months) {
  const rates = extractRates(p)
  const v = rates?.[months]
  if (v === null || v === undefined || v === "") return "-"
  const num = Number(v)
  return Number.isFinite(num) ? `${num.toFixed(2)}%` : String(v)
}

function selectedTermRate(p) {
  const t = selectedMonths.value // 없으면 12
  const rates = extractRates(p)
  const v = rates?.[t]
  const num = Number(v)
  return Number.isFinite(num) ? num : -Infinity
}

const filteredAndSorted = computed(() => {
  let list = [...(products.value || [])]

  if (term.value && onlyWithSelectedTerm.value) {
    const t = Number(term.value)
    list = list.filter((p) => {
      const v = extractRates(p)?.[t]
      const num = Number(v)
      return Number.isFinite(num)
    })
  }

  const dir = sortDir.value === "desc" ? -1 : 1
  list.sort((a, b) => {
    if (sortKey.value === "BANK_ASC") {
      return String(a.kor_co_nm).localeCompare(String(b.kor_co_nm)) * dir
    }
    if (sortKey.value === "NAME_ASC") {
      return String(a.fin_prdt_nm).localeCompare(String(b.fin_prdt_nm)) * dir
    }
    return (selectedTermRate(b) - selectedTermRate(a)) * dir
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

watch([term, onlyWithSelectedTerm, sortKey, sortDir], () => {
  page.value = 1
})

function toggleSortDir() {
  sortDir.value = sortDir.value === "desc" ? "asc" : "desc"
}

function rateClass(p, months) {
  const rates = extractRates(p)

  const v = rates?.[months]
  const num = Number(v)
  if (!Number.isFinite(num)) return "rate-missing"

  const candidates = [6, 12, 24, 36]
    .map((m) => Number(rates?.[m]))
    .filter((x) => Number.isFinite(x))

  const maxRate = candidates.length ? Math.max(...candidates) : -Infinity

  return num === maxRate ? "rate-max" : "rate-base"
}

onMounted(async () => {
  loading.value = true
  error.value = ""
  try {
    await ensureBanksLoaded()
    await fetchProductsList()
  } catch (e) {
    error.value = "데이터를 불러오지 못했습니다."
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.page-title {
  font-weight: 800;
  letter-spacing: -0.4px;
  font-family: "Georgia", "Times New Roman", serif;
  margin-bottom: 4px;
}

.page-kicker {
  text-transform: uppercase;
  letter-spacing: 0.14em;
  font-size: 0.72rem;
  color: #0f766e;
  font-weight: 700;
}

.page-sub {
  color: #64748b;
  margin-bottom: 0;
}

.page-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.page-badge {
  background: rgba(14, 116, 144, 0.08);
  color: #0e7490;
  padding: 8px 14px;
  border-radius: 999px;
  font-weight: 600;
  font-size: 0.85rem;
}

@media (max-width: 991.98px) {
  .page-head {
    flex-direction: column;
    align-items: flex-start;
  }
}

.rate-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 18px;
  padding: 18px;
  box-shadow: 0 18px 40px rgba(15, 23, 42, 0.08);
}

.filters {
  padding: 14px;
  margin-bottom: 12px;
  border-radius: 14px;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
}

.rate-table thead th {
  background: #f1f5f9;
  font-weight: 800;
  font-size: 0.92rem;
  border-bottom: 1px solid #e9ecef;
  white-space: nowrap;
}

.rate-table tbody td {
  border-bottom: 1px solid #f1f3f5;
}

.product-name {
  word-break: keep-all;
}

.row-click {
  cursor: pointer;
}
.row-click:hover {
  background: #fbfcfd;
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
