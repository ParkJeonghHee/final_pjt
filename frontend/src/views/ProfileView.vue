<template>
    <main class="container my-4">
        <div class="p-4 border rounded bg-white mb-3">
            <h4 class="fw-bold mb-0">{{ auth.username }} 님의 프로필</h4>
        </div>

        <div class="border-bottom mb-3 pb-2">
            <a href="#" class="text-decoration-none me-3"
                :class="tab=='info' ? 'fw-bold text-dark' : 'text-muted'"
                @click.prevent="tab='info'">기본 정보 수정</a>
            <span class="text-muted">|</span>

            <a href="#" class="text-decoration-none mx-3"
                :class="tab=='portfolio' ? 'fw-bold text-dark' : 'text-muted'"
                @click.prevent="tab='portfolio'">포트폴리오 수정</a>
            <span class="text-muted">|</span>

            <a href="#" class="text-decoration-none ms-3"
                :class="tab=='recommend' ? 'fw-bold text-dark' : 'text-muted'"
                @click.prevent="tab='recommend'">상품 추천 받기</a>
        </div>

        <div class="p-4 border rounded bg-white">
            <template v-if="tab==='info'">
                <h5 class="fw-bold">기본 정보 수정</h5>
                <p class="text-muted mb-0">나중에 붙일 예정</p>
            </template>

            <template v-else-if="tab==='portfolio'">
                <h5 class="fw-bold">포트폴리오 수정</h5>
                <p class="text-muted mb-0">나중에 붙일 예정</p>
            </template>

            <template v-else>
                <h5 class="fw-bold">상품 추천 받기</h5>
                <p class="text-muted">나중에 붙일 예정</p>
                <button class="btn btn-primary" @click="doRecommend">추천 받기</button>

                <div v-if="result" class="alert alert-success mt-3 mb-0">
                    추천 결과: <b>{{ result }}</b>
                </div>
            </template>
        </div>
    </main>
</template>


<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const tab = ref('info')
const result = ref('')

function doRecommend() {
    result.value = '나중에 알고리즘 적용'
}
</script>