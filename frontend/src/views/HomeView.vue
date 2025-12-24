<template>
  <div>
    <section class="hero-section d-flex align-items-center">
      <div class="container">
        <div class="market-strip mb-4">
          <div class="market-card">
            <div class="market-label">USD/KRW</div>
            <div class="market-value">{{ formatNumber(market.usd) }}</div>
            <div class="market-sub">달러 환율</div>
          </div>
          <div class="market-card">
            <div class="market-label">JPY/KRW</div>
            <div class="market-value">{{ formatNumber(market.jpy) }}</div>
            <div class="market-sub">엔 환율 (100엔)</div>
          </div>
          <div class="market-card">
            <div class="market-label">KR 기준금리</div>
            <div class="market-value">{{ formatPercent(market.baseRate) }}</div>
            <div class="market-sub">대한민국 기준금리</div>
          </div>
          <div class="market-card wide">
            <div class="market-label">국채 3년</div>
            <div class="market-value">{{ formatPercent(market.bond3y) }}</div>
            <div class="market-sub">
              {{ market.detail || "한국은행 ECOS 기준" }}
            </div>
          </div>
        </div>
        <div class="row align-items-center gx-5">
          <div class="col-lg-6 order-2 order-lg-1 text-center text-lg-start">
            <div class="hero-eyebrow mb-3">
              금융 비교 · 분석 플랫폼
            </div>
            <h1 class="display-5 fw-bold mb-4 lh-base">
              스마트한 금융 생활,<br>
              <span class="text-primary">BankBook</span>과 함께
            </h1>
            <p class="lead text-muted mb-5">
              예금, 적금, 대출 상품을 한눈에 비교하고<br class="d-none d-lg-block">
              나에게 딱 맞는 금융 상품을 찾아보세요
            </p>
            <div class="d-flex flex-wrap justify-content-center justify-content-lg-start gap-3">
              <RouterLink to="/deposits" class="btn btn-primary btn-lg px-4 fw-semibold hero-cta">
                상품 비교하기
              </RouterLink>
              <RouterLink to="/stocks" class="btn btn-outline-primary btn-lg px-4 fw-semibold hero-cta ghost">
                더 알아보기
              </RouterLink>
            </div>
          </div>
          <div class="col-lg-6 order-1 order-lg-2 mb-5 mb-lg-0 position-relative hero-media">
            <img src="@/assets/images/hero-image.png" alt="Bankbook Building" class="img-fluid rounded-4 shadow-lg hero-image">
            <div class="card position-absolute top-50 start-0 translate-middle-y p-3 border-0 shadow rounded-4 floating-card">
              <div class="d-flex align-items-center">
                <div class="icon-box bg-primary bg-opacity-10 text-primary rounded-circle me-3">
                  <i class="bi bi-check-lg fs-3"></i>
                </div>
                <div>
                  <p class="small text-muted mb-1">최저 금리</p>
                  <h4 class="fw-bold mb-0">2.5%</h4>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="py-5 bg-white section-features">
      <div class="container py-5">
        <div class="text-center mb-5">
          <h2 class="fw-bold fs-1 mb-3">왜 BankBook을 선택해야 할까요?</h2>
          <p class="text-muted fs-5">편리하고 스마트한 금융 생활을 위한 모든 것</p>
        </div>
        <div class="row g-4">
          <div class="col-md-6 col-lg-4">
            <div class="card h-100 border-0 shadow-sm rounded-4 overflow-hidden hover-lift">
              <img src="@/assets/images/feature-1.png" class="card-img-top" alt="예금 상품 비교">
              <div class="card-body p-4">
                <div class="icon-box bg-primary bg-opacity-10 text-primary rounded-circle mb-4">
                  <i class="bi bi-coin fs-3"></i>
                </div>
                <h4 class="card-title fw-bold mb-3">예금 상품 비교</h4>
                <p class="card-text text-muted mb-4">
                  주요 은행의 예금 상품을 한눈에 비교하고 최고 금리를 찾아보세요
                </p>
                <RouterLink to="/deposits" class="text-decoration-none fw-semibold stretched-link">
                  자세히 보기 <i class="bi bi-arrow-right ms-1"></i>
                </RouterLink>
              </div>
            </div>
          </div>
          <div class="col-md-6 col-lg-4">
            <div class="card h-100 border-0 shadow-sm rounded-4 overflow-hidden hover-lift">
              <img src="@/assets/images/feature-2.png" class="card-img-top" alt="대출 상품 추천">
              <div class="card-body p-4">
                <div class="icon-box bg-primary bg-opacity-10 text-primary rounded-circle mb-4">
                  <i class="bi bi-house-door fs-3"></i>
                </div>
                <h4 class="card-title fw-bold mb-3">대출 상품 추천</h4>
                <p class="card-text text-muted mb-4">
                  조건별 대출 상품을 비교하고 나에게 맞는 대출을 찾아보세요
                </p>
                <RouterLink to="/loans" class="text-decoration-none fw-semibold stretched-link">
                  자세히 보기 <i class="bi bi-arrow-right ms-1"></i>
                </RouterLink>
              </div>
            </div>
          </div>

          <div class="col-md-6 col-lg-4 mx-auto">
            <div class="card h-100 border-0 shadow-sm rounded-4 overflow-hidden hover-lift">
              <img src="@/assets/images/feature-3.png" class="card-img-top" alt="맞춤형 상품 추천" />
              <div class="card-body p-4">
                <div class="icon-box bg-primary bg-opacity-10 text-primary rounded-circle mb-4">
                  <i class="bi bi-check-circle fs-3"></i>
                </div>

                <h4 class="card-title fw-bold mb-3">맞춤형 상품 추천</h4>
                <p class="card-text text-muted mb-4">
                  개인 맞춤형 금융 상품 추천으로 더 나은 선택을 하세요
                </p>

                <a
                  href="#"
                  class="text-decoration-none fw-semibold stretched-link"
                  @click.prevent="goRecommend"
                >
                  자세히 보기 <i class="bi bi-arrow-right ms-1"></i>
                </a>
              </div>
            </div>
          </div>

        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue"
import { useRouter } from "vue-router"
import { useAuthStore } from "@/stores/auth"
import { fetchMarketSummary } from "@/api/market"

const router = useRouter()
const auth = useAuthStore()

const market = ref({
  usd: null,
  jpy: null,
  baseRate: null,
  bond3y: null,
  detail: "",
})
const marketError = ref("")

function formatNumber(value, digits = 2) {
  const num = Number(value)
  if (!Number.isFinite(num)) return "-"
  return num.toLocaleString(undefined, { minimumFractionDigits: digits, maximumFractionDigits: digits })
}

function formatPercent(value) {
  const num = Number(value)
  if (!Number.isFinite(num)) return "-"
  return `${num.toFixed(2)}%`
}

function goRecommend() {
  if (!auth.isLoggedIn) {
    router.push("/login")
    return
  }
  router.push({ path: "/profile", query: { tab: "recommend" } }) 
}

onMounted(async () => {
  try {
    const data = await fetchMarketSummary()
    market.value = {
      usd: data.usd_krw,
      jpy: data.jpy_krw_100,
      baseRate: data.base_rate,
      bond3y: data.bond_3y,
      detail: data.detail || "",
    }
  } catch (e) {
    marketError.value = "시장 정보를 불러오지 못했습니다."
  }
})
</script>


<style scoped>
.hero-section {
  position: relative;
  background: radial-gradient(circle at 20% 20%, #fff7ed 0%, #f8fafc 45%, #eef2f7 100%);
  padding: 70px 0 50px;
  min-height: 60vh;
  overflow: hidden;
}

.market-strip {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.market-card {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(148, 163, 184, 0.35);
  border-radius: 14px;
  padding: 12px 14px;
  backdrop-filter: blur(8px);
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
}

.market-card.wide {
  grid-column: span 1;
}

.market-label {
  font-size: 0.75rem;
  color: #64748b;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.market-value {
  font-size: 1.25rem;
  font-weight: 800;
  color: #0f172a;
}

.market-sub {
  font-size: 0.8rem;
  color: #475569;
}

.hero-section::before {
  content: "";
  position: absolute;
  inset: -20% -10% auto auto;
  width: 520px;
  height: 520px;
  background: radial-gradient(circle, rgba(56, 189, 248, 0.18) 0%, rgba(56, 189, 248, 0) 70%);
  z-index: 0;
}

.hero-section::after {
  content: "";
  position: absolute;
  inset: auto auto -30% -10%;
  width: 460px;
  height: 460px;
  background: radial-gradient(circle, rgba(249, 115, 22, 0.18) 0%, rgba(249, 115, 22, 0) 70%);
  z-index: 0;
}

.hero-section .container {
  position: relative;
  z-index: 1;
}

.hero-eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  border-radius: 999px;
  background: rgba(15, 118, 110, 0.12);
  color: #0f766e;
  font-weight: 600;
  letter-spacing: 0.02em;
  font-size: 0.85rem;
}

.icon-box {
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.hero-cta {
  box-shadow: 0 10px 24px rgba(15, 118, 110, 0.18);
}

.hero-cta.ghost {
  box-shadow: none;
  border-width: 2px;
}

.hero-section h1 {
  font-family: "Trebuchet MS", "Segoe UI", "Helvetica Neue", sans-serif;
  letter-spacing: -0.6px;
}

.hero-image {
  transform: translateY(8px);
}

.floating-card {
  z-index: 10;
  left: -30px !important; 
}

@media (max-width: 991.98px) {
  .hero-section {
    padding: 48px 0 40px;
    text-align: center;
  }
  .market-strip {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .hero-media {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
    margin-top: 8px;
  }
  .floating-card {
    position: static !important;
    transform: none !important;
    margin: 0 auto;
    width: auto;
    white-space: nowrap;
  }
  .hero-image {
    width: 100%;
    max-height: 240px;
    object-fit: cover;
  }
}

@media (max-width: 575.98px) {
  .market-strip {
    grid-template-columns: 1fr;
  }
  .hero-media {
    margin-bottom: 24px;
  }
  .hero-image {
    max-height: 200px;
  }
  .floating-card {
    margin-top: 12px;
  }
}

.hover-lift {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.hover-lift:hover {
  transform: translateY(-10px);
  box-shadow: 0 1rem 3rem rgba(0,0,0,.175) !important;
}
</style>
