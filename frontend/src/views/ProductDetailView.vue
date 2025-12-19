<template>
  <main class="container my-4">
    <div v-if="loading">불러오는 중...</div>
    <div v-else-if="error" class="alert alert-danger">{{ error }}</div>

    <div v-else class="card p-4">
      <h4 class="fw-bold mb-2">{{ product.fin_prdt_nm }}</h4>
      <div class="text-muted mb-3">
        {{ product.kor_co_nm }} · {{ product.product_type === "DEPOSIT" ? "정기예금" : "정기적금" }}
      </div>

      <h6 class="fw-bold">금리 옵션</h6>
      <table class="table">
        <thead>
          <tr>
            <th>기간</th>
            <th>기본금리</th>
            <th>우대금리</th>
            <th>금리유형</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="o in product.options" :key="o.id">
            <td>{{ o.save_trm }}개월</td>
            <td>{{ o.intr_rate }}</td>
            <td>{{ o.intr_rate2 }}</td>
            <td>{{ o.intr_rate_type_nm }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </main>
</template>

<script setup>
import { ref, onMounted } from "vue"
import { useRoute } from "vue-router"
import http from "@/api/http"

const route = useRoute()
const product = ref(null)
const loading = ref(true)
const error = ref("")

onMounted(async () => {
  try {
    const id = route.params.id
    const res = await http.get(`/api/products/${id}/`)
    product.value = res.data
  } catch (e) {
    error.value = "상세 조회 실패"
  } finally {
    loading.value = false
  }
})
</script>
