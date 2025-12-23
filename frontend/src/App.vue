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

          <button
            class="navbar-toggler"
            type="button"
            data-bs-toggle="collapse"
            data-bs-target="#navbarContent"
          >
            <span class="navbar-toggler-icon"></span>
          </button>

          <div class="collapse navbar-collapse justify-content-end" id="navbarContent">
            <div class="navbar-nav gap-4">
              <!-- ✅ 현재 위치(active) 표시용 app-nav-link 클래스 추가 -->
              <RouterLink class="nav-link app-nav-link text-dark fw-semibold" to="/deposits">
                예금비교
              </RouterLink>
              <RouterLink class="nav-link app-nav-link text-dark fw-semibold" to="/metals">
                현물상품
              </RouterLink>
              <RouterLink class="nav-link app-nav-link text-dark fw-semibold" to="/stocks">
                주식정보
              </RouterLink>
              <RouterLink class="nav-link app-nav-link text-dark fw-semibold" to="/map">
                은행지도
              </RouterLink>
              <RouterLink class="nav-link app-nav-link text-dark fw-semibold" to="/community">
                게시판
              </RouterLink>
            </div>
          </div>
        </div>
      </nav>
    </header>

    <main class="flex-grow-1" :class="isMapRoute ? 'main-map' : 'main-default'">
      <RouterView />
      <ChatBotWidget />
    </main>

    <footer
      ref="footerEl"
      class="py-5"
      style="background-color:#0f172a; color:#94a3b8; position:sticky; bottom:0; margin-top:auto;"
    >
      <!-- footer 내용 그대로 -->
      <div class="container">
        <div class="row gy-4">
          <div class="col-lg-4 col-md-6">
            <h5 class="text-white fw-bold mb-3">Bankbook</h5>
            <p class="small mb-4">
              스마트한 금융 생활을 위한<br />
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
              <li><a href="deposits" class="text-decoration-none text-reset">예금 비교</a></li>
              <li><a href="deposits" class="text-decoration-none text-reset">적금 비교</a></li>
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

        <hr class="my-4 border-secondary opacity-25" />

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
import { RouterLink, RouterView, useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import ChatBotWidget from '@/components/ChatBotWidget.vue'
import { computed, onMounted, onBeforeUnmount, ref } from "vue"


const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const isMapRoute = computed(() => route.path === "/map")

const footerEl = ref(null)
let ro = null
let onResize = null

onMounted(() => {
  const setFooterVar = () => {
    const h = footerEl.value?.offsetHeight || 0
    document.documentElement.style.setProperty("--app-footer-offset", `${h}px`)
  }

  setFooterVar()
  ro = new ResizeObserver(setFooterVar)
  if (footerEl.value) ro.observe(footerEl.value)

  onResize = () => setFooterVar()
  window.addEventListener("resize", onResize)
})

onBeforeUnmount(() => {
  if (ro && footerEl.value) ro.unobserve(footerEl.value)
  ro = null
  if (onResize) window.removeEventListener("resize", onResize)
  onResize = null
})

function doLogout() {
  auth.logout()
  router.push("/")
}
</script>

<style scoped>
:global(:root) {
  --app-header-offset: 110px;
  --app-footer-offset: 0px;
}

/* 기본 페이지 */
.main-default {
  padding-top: var(--app-header-offset);
  padding-bottom: 80px;
}

/* ✅ /map 전용: “헤더+푸터를 제외한 영역”을 main 높이로 고정 */
.main-map {
  padding-top: var(--app-header-offset);
  padding-bottom: 0;

  /* footer sticky로 덮는 상황을 원천 차단 */
  height: calc(100vh - var(--app-header-offset) - var(--app-footer-offset));
  overflow: hidden; /* 지도/카드가 footer쪽으로 새지 않게 */
}

/* ✅ 네비 메뉴: 현재 위치(active) 색칠 표시 */
.app-nav-link {
  padding: 8px 14px;
  border-radius: 999px;
  transition: background-color 0.15s ease, color 0.15s ease;
}

/* 정확히 일치하는 경로일 때 (예: /map 일 때 “은행지도”만) */
.app-nav-link.router-link-exact-active {
  color: #0d6efd !important;
  background: rgba(13, 110, 253, 0.12);
}

/* 하위 경로 포함해서도 활성화 표시가 필요하면 아래 유지 (원하지 않으면 삭제 가능)
   예: /deposits/123 에서도 “예금비교”를 활성화 */
.app-nav-link.router-link-active {
  color: #0d6efd !important;
}

.app-nav-link:hover {
  background: rgba(13, 110, 253, 0.08);
}

/* 푸터 링크 호버 효과 */
footer a:hover {
  color: #fff !important;
  transition: color 0.2s;
}
</style>
