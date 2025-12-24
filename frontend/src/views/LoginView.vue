<template>
  <main class="container my-5" style="max-width: 520px;">
    <div class="p-4 border rounded bg-white">
      <h4 class="fw-bold mb-3">로그인</h4>

      <div v-if="error" class="alert alert-danger p-2 mb-3">
        {{ error }}
      </div>

      <div class="mb-3">
        <label class="form-label">아이디</label>
        <input 
          v-model="username" 
          class="form-control" 
          placeholder="아이디를 입력하세요" 
          @keyup.enter="doLogin"
        />
      </div>

      <div class="mb-3">
        <label class="form-label">비밀번호</label>
        <input 
          v-model="password" 
          type="password" 
          class="form-control" 
          placeholder="비밀번호를 입력하세요" 
          @keyup.enter="doLogin"
        />
      </div>

      <button class="btn btn-primary w-100" @click="doLogin">로그인</button>
    </div>
  </main>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

const username = ref('')
const password = ref('')
const error = ref('')

async function doLogin() {
  error.value = ""

  if (!username.value || !password.value) {
    error.value = "아이디와 비밀번호를 모두 입력해주세요."
    return
  }

  try {
    await auth.login(username.value, password.value)
    router.push("/") 
  } catch(e) {
    error.value = "로그인 실패 (아이디 또는 비밀번호 확인)"
  }
}
</script>