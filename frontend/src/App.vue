<template>
  <div>
    <!-- 로그인/회원가입 -->
    <div class="border-bottom bg-white">
      <div class="container py-2 d-flex justify-content-end gap-3 small">
        <template v-if="!auth.isLoggedIn">
          <RouterLink class="text-decoration-none text-muted" to="/login">로그인</RouterLink>
          <span class="text-muted">|</span>
          <RouterLink class="text-decoration-none text-muted" to="/signup">회원가입</RouterLink>
        </template>

      <template v-else>
        <RouterLink class="text-decoration-none text-muted" to="/profile">{{ auth.username }}</RouterLink>
        <span class="text-muted">|</span>
        <a class="text-decoration-none text-muted" href="#" @click.prevent="doLogout">로그아웃</a>
      </template>
      </div>
    </div>


    <!-- 로고 + 메뉴 (예금비교/현무상품/주식정보/은행지도/게시판) -->
    <nav class="bg-white border-bottom">
      <div class="container py-3 d-flex align-items-center justify-content-between">
        <RouterLink class="fw-bold fs-3 text-primary text-decoration-none" to="/">
          BankBook
        </RouterLink>

        <div class="d-none d-md-flex gap-4">
          <RouterLink class="text-decoration-none text-dark" to="/deposits">예금비교</RouterLink>
          <RouterLink class="text-decoration-none text-dark" to="/metals">현물상품</RouterLink>
          <RouterLink class="text-decoration-none text-dark" to="/stocks">주식정보</RouterLink>
          <RouterLink class="text-decoration-none text-dark" to="/map">은행지도</RouterLink>
          <RouterLink class="text-decoration-none text-dark" to="/community">게시판</RouterLink>
        </div>
      </div>
    </nav>
    
    <!-- 페이지 내용 -->
    <RouterView />
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