<template>
  <main class="container my-4">
    <h3 class="fw-bold mb-4">예금 · 적금 비교</h3>

    <!-- ✅ 2번처럼: 좌측 필터 + 우측 테이블 (탭은 우측 테이블 박스 상단으로 이동) -->
    <div class="row g-3">
      <!-- 좌측 필터 패널 -->
      <aside class="col-lg-3">
        <div class="filter-panel p-3">
          <div class="fw-bold mb-2">{{ productTypeLabel }}</div>
          <div class="text-muted small mb-3">검색 조건을 입력하세요</div>

          <div class="mb-2">
            <label class="form-label small mb-1">은행</label>
            <select v-model="bank" class="form-select">
              <option value="전체">전체</option>
              <option v-for="b in banks" :key="b" :value="b">
                {{ b }}
              </option>
            </select>
          </div>

          <div class="mb-2">
            <label class="form-label small mb-1">예치기간</label>
            <select v-model="term" class="form-select">
              <option value="">전체기간</option>
              <option value="6">6개월</option>
              <option value="12">12개월</option>
              <option value="24">24개월</option>
              <option value="36">36개월</option>
            </select>
          </div>

          <div class="mb-3">
            <label class="form-label small mb-1">상품명</label>
            <input
              v-model="q"
              class="form-control"
              placeholder="상품명 검색"
              @keyup.enter="fetchProductsList"
            />
          </div>

          <!-- 추가 기능: 기간 금리 있는 상품만 -->
          <div class="form-check mb-3">
            <input
              class="form-check-input"
              type="checkbox"
              id="onlyWithTerm"
              v-model="onlyWithSelectedTerm"
              :disabled="!term"
            />
            <label class="form-check-label small" for="onlyWithTerm">
              선택 기간 금리 있는 상품만
            </label>
          </div>

          <button type="button" class="btn btn-secondary w-100" @click="fetchProductsList">
            확인
          </button>
        </div>
      </aside>

      <!-- 우측 결과 테이블 -->
      <section class="col-lg-9">
        <!-- 로딩 / 에러 -->
        <div v-if="loading" class="text-center my-5">불러오는 중...</div>
        <div v-else-if="error" class="alert alert-danger">{{ error }}</div>

        <div v-else class="table-wrap">
          <!-- ✅ 탭 + 툴바를 테이블 박스 상단으로 (2번 이미지 느낌) -->
          <div class="table-topbar d-flex flex-wrap align-items-center justify-content-between gap-2 p-2 border-bottom">
            <div class="btn-group btn-group-sm" role="group" aria-label="product type tabs">
              <button
                type="button"
                class="btn"
                :class="productType === 'DEPOSIT' ? 'btn-primary' : 'btn-outline-primary'"
                @click="changeType('DEPOSIT')"
              >
                정기예금
              </button>
              <button
                type="button"
                class="btn"
                :class="productType === 'SAVING' ? 'btn-primary' : 'btn-outline-primary'"
                @click="changeType('SAVING')"
              >
                정기적금
              </button>
            </div>

            <div class="d-flex align-items-center gap-2">
              <div class="text-muted small">
                총 <span class="fw-bold">{{ filteredAndSorted.length }}</span>건
              </div>

              <select v-model="sortKey" class="form-select form-select-sm" style="width: 180px">
                <option value="RATE_DESC">금리 높은순(선택기간)</option>
                <option value="BANK_ASC">은행명 오름차순</option>
                <option value="NAME_ASC">상품명 오름차순</option>
              </select>

              <button class="btn btn-outline-secondary btn-sm" @click="toggleSortDir">
                {{ sortDir === "desc" ? "내림차순" : "오름차순" }}
              </button>
            </div>
          </div>

          <div class="table-responsive">
            <table class="table table-hover align-middle mb-0">
              <thead class="table-head">
                <tr>
                  <th style="width: 180px">금융회사명</th>
                  <th>상품명</th>
                  <th class="text-end" style="width: 90px">6개월</th>
                  <th class="text-end" style="width: 90px">12개월</th>
                  <th class="text-end" style="width: 90px">24개월</th>
                  <th class="text-end" style="width: 90px">36개월</th>
                </tr>
              </thead>

              <tbody>
                <tr
                  v-for="p in pagedItems"
                  :key="p.id"
                  class="clickable-row"
                  @click="goDetail(p.id)"
                >
                  <td class="fw-semibold">{{ p.kor_co_nm }}</td>
                  <td>{{ p.fin_prdt_nm }}</td>

                  <td class="text-end">{{ rateText(p, 6) }}</td>
                  <td class="text-end">{{ rateText(p, 12) }}</td>
                  <td class="text-end">{{ rateText(p, 24) }}</td>
                  <td class="text-end">{{ rateText(p, 36) }}</td>
                </tr>

                <tr v-if="filteredAndSorted.length === 0">
                  <td colspan="6" class="text-center text-muted py-4">
                    검색 결과가 없습니다.
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- 페이지네이션 -->
          <div class="d-flex justify-content-end align-items-center gap-2 p-2 border-top">
            <button class="btn btn-outline-secondary btn-sm" :disabled="page === 1" @click="page--">
              이전
            </button>
            <div class="small text-muted">
              {{ page }} / {{ totalPages }}
            </div>
            <button
              class="btn btn-outline-secondary btn-sm"
              :disabled="page === totalPages"
              @click="page++"
            >
              다음
            </button>
          </div>
        </div>
      </section>
    </div>
  </main>
</template>

<script setup>
import { ref, onMounted, computed, watch } from "vue"
import { useRouter } from "vue-router"
import { fetchProducts, fetchBanks, syncProducts } from "@/api/products"

const router = useRouter()

/* 상태 */
const products = ref([])
const banks = ref([])

const loading = ref(false)
const error = ref("")

const productType = ref("DEPOSIT") // DEPOSIT | SAVING
const bank = ref("전체")
const term = ref("")
const q = ref("")

/* 추가 UX 상태 */
const onlyWithSelectedTerm = ref(false)
const sortKey = ref("RATE_DESC") // RATE_DESC | BANK_ASC | NAME_ASC
const sortDir = ref("desc") // desc | asc

const page = ref(1)
const pageSize = ref(10)

const productTypeLabel = computed(() => (productType.value === "DEPOSIT" ? "정기예금" : "정기적금"))

/* 은행 목록 로딩 + (필요시) 자동 sync */
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

/* 상품 목록 조회(서버 필터 기반 유지) */
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

/* 탭 변경 */
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

/* 상세 페이지 이동 */
function goDetail(id) {
  router.push(`/products/${id}`)
}

/* -----------------------------
   ✅ 금리 파싱 (안전하게)
-------------------------------- */
function extractRates(p) {
  // 서버가 평탄화해서 내려주는 경우(있으면 그대로 사용)
  const flat = {
    6: p.rate_6 ?? p.intr_rate_6,
    12: p.rate_12 ?? p.intr_rate_12,
    24: p.rate_24 ?? p.intr_rate_24,
    36: p.rate_36 ?? p.intr_rate_36,
  }

  const hasAnyFlat = Object.values(flat).some((v) => v !== undefined && v !== null && v !== "")
  if (hasAnyFlat) return flat

  // 옵션 배열 추정
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

    // 우대금리(intr_rate2)가 있으면 그걸 우선 표시, 없으면 기본금리
    const r = opt.intr_rate2 ?? opt.intr_rate ?? opt.rate ?? null
    if (r === null || r === undefined || r === "") continue

    // 같은 기간이 여러개면 최대값 표시
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
  return Number.isFinite(num) ? num.toFixed(2) : String(v)
}

function selectedTermRate(p) {
  const t = Number(term.value || 12) // 선택기간 없으면 12 기준으로 정렬
  const rates = extractRates(p)
  const v = rates?.[t]
  const num = Number(v)
  return Number.isFinite(num) ? num : -Infinity
}

/* -----------------------------
   ✅ 클라이언트 추가 기능:
   - (옵션) 선택기간 금리 있는 상품만
   - 정렬
-------------------------------- */
const filteredAndSorted = computed(() => {
  let list = [...(products.value || [])]

  // 선택기간 금리 있는 상품만(옵션)
  if (term.value && onlyWithSelectedTerm.value) {
    const t = Number(term.value)
    list = list.filter((p) => {
      const v = extractRates(p)?.[t]
      const num = Number(v)
      return Number.isFinite(num)
    })
  }

  // 정렬
  const dir = sortDir.value === "desc" ? -1 : 1
  list.sort((a, b) => {
    if (sortKey.value === "BANK_ASC") {
      return String(a.kor_co_nm).localeCompare(String(b.kor_co_nm)) * dir
    }
    if (sortKey.value === "NAME_ASC") {
      return String(a.fin_prdt_nm).localeCompare(String(b.fin_prdt_nm)) * dir
    }
    // RATE_DESC(선택기간 기준)
    return (selectedTermRate(b) - selectedTermRate(a)) * dir
  })

  return list
})

/* 페이지네이션 */
const totalPages = computed(() => Math.max(1, Math.ceil(filteredAndSorted.value.length / pageSize.value)))
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

/* 최초 로딩 */
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
/* 좌측 패널: 색상은 크게 건드리지 않고(배경/테두리 위주) 구조만 */
.filter-panel {
  border: 1px solid #e9ecef;
  border-radius: 10px;
  background: #fff;
}

/* 테이블 래퍼 */
.table-wrap {
  border: 1px solid #e9ecef;
  border-radius: 10px;
  overflow: hidden;
  background: #fff;
}

/* ✅ 테이블 상단 헤더 바(탭/툴바가 들어가는 영역) */
.table-topbar {
  background: #fff; /* 색상 변경 없이 유지 */
}

/* 헤더는 너무 튀지 않게(색 톤 유지) */
.table-head th {
  background: #f8f9fa;
  font-weight: 700;
  font-size: 0.9rem;
}

/* 행 클릭 UX */
.clickable-row {
  cursor: pointer;
}
.clickable-row:hover {
  background-color: #f8f9fa;
}
</style>
