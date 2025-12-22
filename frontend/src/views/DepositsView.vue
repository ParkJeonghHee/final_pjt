<template>
  <main class="container my-4">
    <!-- 타이틀 -->
    <h3 class="fw-bold mb-4">예금 · 적금 비교</h3>

    <!-- 상품 타입 선택 -->
    <div class="btn-group mb-3">
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

    <!-- 필터 영역 -->
    <div class="row g-2 mb-4">
      <div class="col-md-3">
        <select v-model="bank" class="form-select">
          <option value="전체">전체 은행</option>
          <option v-for="b in banks" :key="b" :value="b">
            {{ b }}
          </option>
        </select>
      </div>

      <div class="col-md-3">
        <select v-model="term" class="form-select">
          <option value="">전체 기간</option>
          <option value="6">6개월</option>
          <option value="12">12개월</option>
          <option value="24">24개월</option>
          <option value="36">36개월</option>
        </select>
      </div>

      <div class="col-md-4">
        <input
          v-model="q"
          class="form-control"
          placeholder="상품명 검색"
          @keyup.enter="fetchProductsList"
        />
      </div>

      <div class="col-md-2">
        <button
          type="button"
          class="btn btn-secondary w-100"
          @click="fetchProductsList"
        >
          검색
        </button>
      </div>
    </div>

    <!-- 로딩 / 에러 -->
    <div v-if="loading" class="text-center my-5">
      불러오는 중...
    </div>

    <div v-else-if="error" class="alert alert-danger">
      {{ error }}
    </div>

    <!-- 상품 목록 -->
    <div v-else>
      <div
        v-for="p in products"
        :key="p.id"
        class="card p-3 mb-2 product-card"
        role="button"
        @click="goDetail(p.id)"
      >
        <div class="fw-bold">{{ p.kor_co_nm }}</div>
        <div>{{ p.fin_prdt_nm }}</div>
      </div>

      <div v-if="products.length === 0" class="text-muted text-center mt-4">
        검색 결과가 없습니다.
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref, onMounted } from "vue"
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

/* 은행 목록 로딩 + (필요시) 자동 sync */
async function ensureBanksLoaded() {
  // 1) 은행 목록 먼저 요청 (DB 기반)
  let bankList = await fetchBanks(productType.value)

  // bankList가 [] 이거나 ["전체"]만 있는 경우(네 백엔드 로직에 따라 조정)
  const isEmpty =
    !bankList || bankList.length === 0 || (bankList.length === 1 && bankList[0] === "전체")

  // 2) 비어있으면 sync 실행 후 다시 요청
  if (isEmpty) {
    await syncProducts()
    bankList = await fetchBanks(productType.value)
  }

  // 3) "전체" 항목은 select에서 고정으로 넣고 있으니, 서버가 포함해서 주면 제거
  banks.value = (bankList || []).filter((b) => b !== "전체")
}

/* 상품 목록 조회 */
async function fetchProductsList() {
  loading.value = true
  error.value = ""

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

/* 탭 변경: 타입 바뀌면 은행 목록/상품 목록 재로딩 */
async function changeType(type) {
  if (productType.value === type) return

  productType.value = type
  bank.value = "전체"
  term.value = ""
  q.value = ""

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
.product-card:hover {
  background-color: #f8f9fa;
}
</style>
