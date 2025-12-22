<template>
    <main class="container my-4">
        <div class="p-4 border rounded bg-white mb-3">
            <h4 class="fw-bold mb-0">{{ auth.username }} 님의 프로필</h4>
        </div>

        <div class="border-bottom mb-3 pb-2">
            <a href="#" class="text-decoration-none tab-link"
                :class="tab === 'info' ? 'fw-bold text-dark' : 'text-muted'"
                @click.prevent="tab = 'info'">기본 정보 수정</a>
            <span class="divider">  |  </span>

            <a href="#" class="text-decoration-none tab-link"
                :class="tab === 'portfolio' ? 'fw-bold text-dark' : 'text-muted'"
                @click.prevent="tab = 'portfolio'">포트폴리오 수정</a>
            <span class="divider">  |  </span>

            <a href="#" class="text-decoration-none tab-link"
                :class="tab === 'recommend' ? 'fw-bold text-dark' : 'text-muted'"
                @click.prevent="tab = 'recommend'">상품 추천 받기</a>
            <span class="divider">  |  </span>

            <a href="#" class="text-decoration-none tab-link"
                :class="tab === 'videos' ? 'fw-bold text-dark' : 'text-muted'"
                @click.prevent="tab = 'videos'">관심 동영상</a>
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

            <template v-else-if="tab==='recommend'">
                <h5 class="fw-bold">상품 추천 받기</h5>
                <p class="text-muted">나중에 붙일 예정</p>
                <button class="btn btn-primary" @click="doRecommend">추천 받기</button>

                <div v-if="result" class="alert alert-success mt-3 mb-0">
                    추천 결과: <b>{{ result }}</b>
                </div>
            </template>

            <template v-else-if="tab === 'videos'">
            <h5 class="fw-bold">관심 동영상</h5>
            <p class="text-muted mb-3">저장한 관심 동영상 목록</p>

            <div v-if="videos.length === 0" class="text-muted">
                아직 저장된 동영상이 없습니다.
            </div>

            <ul v-else class="list-group">
                <li
                v-for="v in videos"
                :key="v.id"
                class="list-group-item"
                >
                <div class="d-flex gap-3 align-items-start">
                    <!-- ✅ 썸네일 -->
                    <a :href="v.url" target="_blank" rel="noopener">
                    <img
                        :src="getThumb(v)"
                        :alt="v.title"
                        style="width: 160px; height: 90px; object-fit: cover; border-radius: 8px;"
                    />
                    </a>

                    <!-- ✅ 정보 -->
                    <div class="flex-grow-1">
                    <div class="fw-semibold mb-1">{{ v.title }}</div>
                    <div v-if="v.channelTitle" class="text-muted small">
                        채널명: {{ v.channelTitle }}
                    </div>
                    <div v-if="v.publishedAt" class="text-muted small mb-2">
                        업로드 날짜: {{ v.publishedAt }}
                    </div>
                    <a :href="v.url" target="_blank" rel="noopener" class="small">
                        {{ v.url }}
                    </a>
                    </div>

                    <!-- ✅ 삭제 -->
                    <button class="btn btn-outline-danger btn-sm" @click="removeVideo(v.id)">
                    삭제
                    </button>
                </div>
                </li>
            </ul>
            </template>
        </div>
        
    </main>
</template>


<script setup>
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useSavedVideosStore } from '@/stores/savedVideos' // ✅ 관심동영상 저장소

const auth = useAuthStore()
const tab = ref('info')
const result = ref('')

const savedStore = useSavedVideosStore()
const videos = computed(() => savedStore.list)

function removeVideo(id) {
  savedStore.remove(id)
}

function getThumb(v) {
  if (v.thumbnail) return v.thumbnail
  return `https://i.ytimg.com/vi/${v.id}/hqdefault.jpg`
}

function doRecommend() {
  result.value = '나중에 알고리즘 적용'
}
</script>
