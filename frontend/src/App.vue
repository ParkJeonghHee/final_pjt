<template>
  <div class="d-flex flex-column min-vh-100">
    <header class="fixed-top bg-white shadow-sm">
      <div class="border-bottom">
        <div class="container py-2 d-flex justify-content-end gap-3 small">
          <template v-if="!auth.isLoggedIn">
            <RouterLink class="text-decoration-none text-muted" to="/login">로그인</RouterLink>
            <span class="text-muted">|</span>
            <RouterLink class="text-decoration-none text-muted" to="/signup">회원가입</RouterLink>
          </template>

          <template v-else>
            <RouterLink class="text-decoration-none text-muted" to="/profile">
              <span class="fw-bold">{{ auth.username }}</span>님
            </RouterLink>
            <span class="text-muted">|</span>
            <a class="text-decoration-none text-muted" href="#" @click.prevent="doLogout">로그아웃</a>
          </template>
        </div>
      </div>

      <nav class="navbar navbar-expand-md bg-white">
        <div class="container py-2">
          <RouterLink class="navbar-brand fw-bold fs-3 text-primary" to="/">
            Bankbook
          </RouterLink>

          <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarContent">
            <span class="navbar-toggler-icon"></span>
          </button>

          <div class="collapse navbar-collapse justify-content-end" id="navbarContent">
            <div class="navbar-nav gap-4">
              <RouterLink class="nav-link text-dark fw-semibold" to="/deposits">예금비교</RouterLink>
              <RouterLink class="nav-link text-dark fw-semibold" to="/metals">현물상품</RouterLink>
              <RouterLink class="nav-link text-dark fw-semibold" to="/stocks">주식정보</RouterLink>
              <RouterLink class="nav-link text-dark fw-semibold" to="/map">은행지도</RouterLink>
              <RouterLink class="nav-link text-dark fw-semibold" to="/community">게시판</RouterLink>
            </div>
          </div>
        </div>
      </nav>
    </header>

    <main class="flex-grow-1" style="padding-top: 110px;">
      <RouterView />
    </main>

    <footer class="py-5" style="background-color: #0f172a; color: #94a3b8;">
      <div class="container">
        <div class="row gy-4">
          <div class="col-lg-4 col-md-6">
            <h5 class="text-white fw-bold mb-3">Bankbook</h5>
            <p class="small mb-4">
              스마트한 금융 생활을 위한<br>
              최고의 파트너
            </p>
            <div class="d-flex gap-3">
              <a href="#" class="text-decoration-none text-secondary"><i class="bi bi-facebook"></i> F</a>
              <a href="#" class="text-decoration-none text-secondary"><i class="bi bi-twitter"></i> T</a>
              <a href="#" class="text-decoration-none text-secondary"><i class="bi bi-instagram"></i> I</a>
            </div>
          </div>

          <div class="col-lg-2 col-md-6">
            <h6 class="text-white fw-bold mb-3">상품</h6>
            <ul class="list-unstyled small d-flex flex-column gap-2">
              <li><a href="#" class="text-decoration-none text-reset">예금 비교</a></li>
              <li><a href="#" class="text-decoration-none text-reset">적금 비교</a></li>
              <li><a href="#" class="text-decoration-none text-reset">대출 상품</a></li>
              <li><a href="#" class="text-decoration-none text-reset">신용카드</a></li>
            </ul>
          </div>

          <div class="col-lg-2 col-md-6">
            <h6 class="text-white fw-bold mb-3">고객지원</h6>
            <ul class="list-unstyled small d-flex flex-column gap-2">
              <li><a href="#" class="text-decoration-none text-reset">자주 묻는 질문</a></li>
              <li><a href="#" class="text-decoration-none text-reset">고객센터</a></li>
              <li><a href="#" class="text-decoration-none text-reset">이용약관</a></li>
              <li><a href="#" class="text-decoration-none text-reset">개인정보처리방침</a></li>
            </ul>
          </div>

          <div class="col-lg-2 col-md-6">
            <h6 class="text-white fw-bold mb-3">회사</h6>
            <ul class="list-unstyled small d-flex flex-column gap-2">
              <li><a href="#" class="text-decoration-none text-reset">회사 소개</a></li>
              <li><a href="#" class="text-decoration-none text-reset">채용</a></li>
              <li><a href="#" class="text-decoration-none text-reset">제휴 문의</a></li>
              <li><a href="#" class="text-decoration-none text-reset">공지사항</a></li>
            </ul>
          </div>
        </div>

        <hr class="my-4 border-secondary opacity-25">

        <div class="d-flex flex-column flex-md-row justify-content-between align-items-center small">
          <p class="mb-0">© 2024 Bankbook. All rights reserved.</p>
          <div class="d-flex gap-3 mt-2 mt-md-0">
            <a href="#" class="text-decoration-none text-reset">개인정보처리방침</a>
            <a href="#" class="text-decoration-none text-reset">이용약관</a>
            <a href="#" class="text-decoration-none text-reset">쿠키 설정</a>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { RouterLink, RouterView, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

function doLogout() {
  auth.logout()
  router.push('/')
}


</script>

<style scoped>
/* 푸터 링크 호버 효과 */
footer a:hover {
  color: #fff !important;
  transition: color 0.2s;
}
</style>