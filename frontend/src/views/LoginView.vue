<template>
    <main class="container my-5" style="max-width: 520px;">
        <div class="p-4 border rounded bg-white">
            <h4 class="fw-bold mb-3">로그인</h4>

            <div class="mb-3">
                <label class="form-label">아이디</label>
                <input v-model="username" class="form-control" placeholder="test" />
            </div>

            <div class="mb-3">
                <label class="form-label">비밀번호</label>
                <input v-model="password" type="password" class="form-control" placeholder="임시" />
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

const username = ref('test')
const password = ref('')

function doLogin() {
    auth.login(username.value)
    router.push('/profile')
}
</script>