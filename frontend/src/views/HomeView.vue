<template>
  <div>
    <section class="hero-section d-flex align-items-center">
      <div class="container">
        <div class="row align-items-center gx-5">
          <div class="col-lg-6 order-2 order-lg-1 text-center text-lg-start">
            <h1 class="display-5 fw-bold mb-4 lh-base">
              스마트한 금융 생활,<br>
              <span class="text-primary">Bankbook</span>과 함께
            </h1>
            <p class="lead text-muted mb-5">
              예금, 적금, 대출 상품을 한눈에 비교하고<br class="d-none d-lg-block">
              나에게 딱 맞는 금융 상품을 찾아보세요
            </p>
            <div class="d-flex justify-content-center justify-content-lg-start gap-3">
              <RouterLink to="/deposits" class="btn btn-primary btn-lg px-4 fw-semibold">상품 비교하기</RouterLink>
              <RouterLink to="/about" class="btn btn-outline-primary btn-lg px-4 fw-semibold">더 알아보기</RouterLink>
            </div>
          </div>
          <div class="col-lg-6 order-1 order-lg-2 mb-5 mb-lg-0 position-relative">
            <img src="@/assets/images/hero-image.png" alt="Bankbook Building" class="img-fluid rounded-4 shadow-lg">
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
          <h2 class="fw-bold fs-1 mb-3">왜 Bankbook을 선택해야 할까요?</h2>
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
              <img src="@/assets/images/feature-3.png" class="card-img-top" alt="맞춤형 상품 추천">
              <div class="card-body p-4">
                <div class="icon-box bg-primary bg-opacity-10 text-primary rounded-circle mb-4">
                  <i class="bi bi-check-circle fs-3"></i>
                </div>
                <h4 class="card-title fw-bold mb-3">맞춤형 상품 추천</h4>
                <p class="card-text text-muted mb-4">
                  개인 맞춤형 금융 상품 추천으로 더 나은 선택을 하세요
                </p>
                <RouterLink to="/recommendations" class="text-decoration-none fw-semibold stretched-link">
                  자세히 보기 <i class="bi bi-arrow-right ms-1"></i>
                </RouterLink>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
/* Hero 섹션 배경 그라데이션 */
.hero-section {
  background: linear-gradient(135deg, #f6f9fc 0%, #eef2f7 100%);
  padding: 100px 0; /* 상하 여백 */
  min-height: 80vh; /* 최소 높이 설정 */
}

/* 아이콘 박스 공통 스타일 */
.icon-box {
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 플로팅 카드 위치 조정 */
.floating-card {
  z-index: 10;
  left: -30px !important; /* 이미지 위로 살짝 겹치게 */
}

/* 모바일 환경에서 플로팅 카드 위치 조정 */
@media (max-width: 991.98px) {
  .hero-section {
    padding: 60px 0;
    text-align: center;
  }
  .floating-card {
    left: 50% !important;
    transform: translate(-50%, -50%) !important;
    top: 0 !important;
    width: auto;
    white-space: nowrap;
  }
}

/* 카드 호버 효과 */
.hover-lift {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.hover-lift:hover {
  transform: translateY(-10px);
  box-shadow: 0 1rem 3rem rgba(0,0,0,.175) !important;
}
</style>