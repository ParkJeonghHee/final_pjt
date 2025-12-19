<template>
  <main class="container my-5" style="max-width: 520px;">
    <div class="card p-4">
      <h3 class="fw-bold mb-3">회원가입</h3>

      <div v-if="error" class="alert alert-danger">{{ error }}</div>
      <div v-if="success" class="alert alert-success">{{ success }}</div>

      <form @submit.prevent="submit">
        <div class="mb-3">
          <label class="form-label">아이디(username)</label>
          <input v-model="form.username" class="form-control" required />
        </div>

        <div class="mb-3">
          <label class="form-label">비밀번호</label>
          <input v-model="form.password" type="password" class="form-control" required />
        </div>

        <div class="mb-3">
          <label class="form-label">이메일</label>
          <input v-model="form.email" type="email" class="form-control" />
        </div>

        <div class="mb-3">
          <label class="form-label">닉네임</label>
          <input v-model="form.nickname" class="form-control" />
        </div>

        <div class="mb-3">
          <label class="form-label">나이</label>
          <input v-model.number="form.age" type="number" class="form-control" />
        </div>

        <div class="mb-3">
          <label class="form-label">총자산</label>
          <input v-model.number="form.total_assets" type="number" class="form-control" />
        </div>

        <div class="mb-4">
          <label class="form-label">월소득</label>
          <input v-model.number="form.income" type="number" class="form-control" />
        </div>

        <button class="btn btn-primary w-100" :disabled="loading">
          {{ loading ? "가입 중..." : "회원가입" }}
        </button>
      </form>
    </div>
  </main>
</template>

<script setup>
import { reactive, ref } from "vue"
import { useRouter } from "vue-router"
import http from "@/api/http"

const router = useRouter()
const loading = ref(false)
const error = ref("")
const success = ref("")

const form = reactive({
  username: "",
  password: "",
  email: "",
  nickname: "",
  age: null,
  total_assets: null,
  income: null,
})

async function submit() {
  error.value = ""
  success.value = ""
  loading.value = true

  try {
    await http.post("/api/accounts/signup/", form)
    success.value = "회원가입 성공 \n 로그인 페이지로 이동합니다."
    setTimeout(() => router.push("/login"), 700)
  } catch (e) {
    const data = e?.response?.data
    if (data) error.value = JSON.stringify(data)
    else error.value = "회원가입 실패"
  } finally {
    loading.value = false
  }
}
</script>
