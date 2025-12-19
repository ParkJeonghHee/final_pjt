<template>
  <main class="container my-4">
    <!-- 타이틀 -->
    <h3 class="fw-bold mb-4">예금 · 적금 비교</h3>

    <!-- 상품 타입 선택 -->
    <div class="btn-group mb-3">
      <button
        class="btn"
        :class="productType === 'DEPOSIT' ? 'btn-primary' : 'btn-outline-primary'"
        @click="changeType('DEPOSIT')"
      >
        정기예금
      </button>
      <button
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
        />
      </div>

      <div class="col-md-2">
        <button class="btn btn-secondary w-100" @click="fetchProducts">
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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/api/http'

const router = useRouter()

/* 상태 */
const products = ref([])
const loading = ref(false)
const error = ref('')

const productType = ref('DEPOSIT') // DEPOSIT | SAVING
const bank = ref('전체')
const term = ref('')
const q = ref('')

const banks = ref([])

/* 목록 조회 */
async function fetchProducts() {
  loading.value = true
  error.value = ''

  try {
    const res = await http.get('/api/products/', {
      params: {
        type: productType.value,
        bank: bank.value,
        term: term.value,
        q: q.value,
      },
    })

    products.value = res.data

    // 은행 목록 자동 추출
    banks.value = [...new Set(res.data.map(p => p.kor_co_nm))]
  } catch (e) {
    error.value = '상품 목록을 불러오지 못했습니다.'
  } finally {
    loading.value = false
  }
}

/* 상품 타입 변경 */
function changeType(type) {
  productType.value = type
  fetchProducts()
}

/* 상세 페이지 이동 */
function goDetail(id) {
  router.push(`/products/${id}`)
}

/* 최초 로딩 */
onMounted(fetchProducts)
</script>

<style scoped>
.product-card:hover {
  background-color: #f8f9fa;
}
</style>
