<template>
  <div>
    <h5 class="fw-bold mb-2">상품 추천 받기</h5>
    <p class="text-muted mb-3">
      사용자 정보(나이/소득/자산)와 미가입 상품/우대금리 상위 후보군을 기반으로 추천합니다.
    </p>

    <!-- 버튼 영역: 예금(파랑) / 대출(초록)로 시각 구분 -->
    <div class="d-flex flex-wrap gap-2">
      <button class="btn btn-outline-primary" :disabled="recommendLoading" @click="doRecommend">
        {{ recommendLoading ? "추천 생성 중..." : "예금/적금 추천 받기" }}
      </button>
      <button class="btn btn-outline-success" :disabled="loanRecommendLoading" @click="doLoanRecommend">
        {{ loanRecommendLoading ? "추천 생성 중..." : "대출 추천 받기" }}
      </button>
    </div>

    <!-- 에러 -->
    <p v-if="recommendError" class="text-danger fw-semibold mt-2 mb-0">
      {{ recommendError }}
    </p>
    <p v-if="loanRecommendError" class="text-danger fw-semibold mt-2 mb-0">
      {{ loanRecommendError }}
    </p>

    <!-- ✅ 결과 영역: 카드 2개로 확실히 분리 -->
    <div class="mt-3 d-grid gap-3">
      <!-- 예금/적금 섹션 -->
      <section v-if="recommendSummary || recommendedList.length" class="result-card result-card--deposit">
        <div class="result-card__head">
          <div class="d-flex align-items-center gap-2">
            <span class="badge text-bg-primary">예금/적금</span>
            <span class="fw-bold">추천 결과</span>
            <span v-if="recommendedList.length" class="text-muted small">({{ recommendedList.length }}개)</span>
          </div>
        </div>

        <div class="result-card__body">
          <div v-if="recommendSummary" class="alert alert-secondary mb-3">
            {{ recommendSummary }}
          </div>

          <div v-if="recommendedList.length">
            <div class="p-3 border rounded bg-white mb-2" v-for="(r, idx) in recommendedList" :key="r.id">
              <div class="fw-semibold d-flex justify-content-between align-items-start gap-2">
                <div class="me-2">
                  {{ idx + 1 }}) {{ r.name }}
                </div>
                <RouterLink class="btn btn-outline-primary btn-sm" :to="`/products/${r.id}`">
                  상세보기
                </RouterLink>
              </div>
              <div class="text-muted mt-1">이유: {{ r.reason }}</div>
            </div>
          </div>
        </div>
      </section>

      <!-- 대출 섹션 -->
      <section v-if="loanRecommendSummary || loanRecommendedList.length" class="result-card result-card--loan">
        <div class="result-card__head">
          <div class="d-flex align-items-center gap-2">
            <span class="badge text-bg-success">대출</span>
            <span class="fw-bold">추천 결과</span>
            <span v-if="loanRecommendedList.length" class="text-muted small">({{ loanRecommendedList.length }}개)</span>
          </div>
        </div>

        <div class="result-card__body">
          <div v-if="loanRecommendSummary" class="alert alert-secondary mb-3">
            {{ loanRecommendSummary }}
          </div>

          <div v-if="loanRecommendedList.length">
            <div
              class="p-3 border rounded bg-white mb-2"
              v-for="(r, idx) in loanRecommendedList"
              :key="r.fin_prdt_cd"
            >
              <div class="fw-semibold d-flex justify-content-between align-items-start gap-2">
                <div class="me-2">
                  {{ idx + 1 }}) {{ r.name }}
                </div>

                <RouterLink
                  class="btn btn-outline-success btn-sm"
                  :to="{ path: `/loans/${r.fin_prdt_cd}`, query: { category: r.category } }"
                >
                  상세보기
                </RouterLink>
              </div>
              <div class="text-muted mt-1">이유: {{ r.reason }}</div>
            </div>
          </div>
        </div>
      </section>

      <!-- 아무것도 없을 때 -->
      <div
        v-if="
          !recommendLoading &&
          !loanRecommendLoading &&
          !recommendedList.length &&
          !loanRecommendedList.length &&
          !recommendSummary &&
          !loanRecommendSummary &&
          !recommendError &&
          !loanRecommendError
        "
        class="text-muted"
      >
        아직 추천을 실행하지 않았습니다.
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue"
import http from "@/api/http"

const recommendLoading = ref(false)
const recommendError = ref("")
const recommendSummary = ref("")
const recommendedList = ref([])
const loanRecommendLoading = ref(false)
const loanRecommendError = ref("")
const loanRecommendSummary = ref("")
const loanRecommendedList = ref([])

async function doRecommend() {
  recommendLoading.value = true
  recommendError.value = ""
  recommendSummary.value = ""
  recommendedList.value = []

  try {
    const res = await http.post("/api/recommend/")
    const data = res?.data || {}

    recommendedList.value = Array.isArray(data.recommended) ? data.recommended : []
    recommendSummary.value = data.summary || ""

    if (!recommendedList.value.length && !recommendSummary.value) {
      recommendSummary.value = "추천 결과가 없습니다."
    }
  } catch (e) {
    const status = e?.response?.status
    if (status === 401 || status === 403) {
      recommendError.value = "로그인이 필요합니다. (토큰 확인)"
    } else {
      recommendError.value = "추천 요청에 실패했습니다. (서버 로그/네트워크 확인)"
    }
  } finally {
    recommendLoading.value = false
  }
}

async function doLoanRecommend() {
  loanRecommendLoading.value = true
  loanRecommendError.value = ""
  loanRecommendSummary.value = ""
  loanRecommendedList.value = []

  try {
    const res = await http.post("/api/loans/recommend/")
    const data = res?.data || {}

    loanRecommendedList.value = Array.isArray(data.recommended) ? data.recommended : []
    loanRecommendSummary.value = data.summary || ""

    if (!loanRecommendedList.value.length && !loanRecommendSummary.value) {
      loanRecommendSummary.value = "추천 결과가 없습니다."
    }
  } catch (e) {
    const status = e?.response?.status
    if (status === 401 || status === 403) {
      loanRecommendError.value = "로그인이 필요합니다. (토큰 확인)"
    } else {
      loanRecommendError.value = "대출 추천 요청에 실패했습니다. (서버 로그/네트워크 확인)"
    }
  } finally {
    loanRecommendLoading.value = false
  }
}
</script>

<style scoped>
/* 결과 섹션 카드 */
.result-card {
  border: 1px solid #e9ecef;
  border-radius: 14px;
  overflow: hidden;
  background: #fff;
}

.result-card__head {
  padding: 12px 14px;
  border-bottom: 1px solid #eef1f3;
}

.result-card__body {
  padding: 12px 14px;
}

/* 섹션별 포인트(헤더 배경 + 왼쪽 라인) */
.result-card--deposit .result-card__head {
  background: rgba(13, 110, 253, 0.06);
  border-left: 6px solid #0d6efd;
}

.result-card--loan .result-card__head {
  background: rgba(25, 135, 84, 0.06);
  border-left: 6px solid #198754;
}
</style>
