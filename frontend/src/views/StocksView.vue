<template>
  <main class="container my-5">
    <div class="p-4 border rounded bg-white">
      <h4 class="fw-bold mb-3">관심 종목 관련 영상 검색</h4>

      <!-- 검색 UI -->
      <div class="d-flex gap-2 mb-3 align-items-stretch">
        <input 
          v-model.trim="q"
          class="form-control"
          type="text"
          placeholder="검색어를 입력하세요"
          @keyup.enter="onSearch" />
        <button class="btn btn-success search-btn" @click="onSearch" :disabled="loading">
          검색
        </button>
      </div>

      <!-- 안내, 에러 -->
      <p v-if="errorMsg" class="text-danger fw-semibold mb-3">
        {{ errorMsg }}
      </p>

      <div v-if="loading" class="text-muted">불러오는 중...</div>

      <div v-else-if="videos.length === 0" class="text-muted">
        검색 결과가 없습니다.
      </div>

      <!-- 결과 -->
      <div v-else class="row g-3">
        <div class="col-md-4" v-for="v in videos" :key="v.videoId">
          <div
            class="card h-100"
            role="button"
            @click="goDetail(v.videoId)">
            <img :src="v.thumbnail" class="card-img-top" alt="thumbnail" />
            <div class="card-body">
              <div class="fw-bold mb-1" style="font-size: 0.95rem;">
                {{ v.title }}
              </div>
              <div class="text-muted small">
                {{ v.channelTitle }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>


<script setup>
import { ref } from "vue"
import { useRouter }from "vue-router"
import { searchYoutubeVideos } from "@/api/youtube"

const router = useRouter()

const q = ref("")
const videos = ref([])
const loading = ref(false)
const errorMsg = ref("")

function goDetail(videoId) {
  router.push(`/stocks/${videoId}`)
}

async function onSearch() {
  errorMsg.value = ""
  videos.value = []

  if (!q.value) {
    errorMsg.value = "검색어를 입력하세요."
    return
  }

  loading.value = true
  try {
    const res = await searchYoutubeVideos(q.value)
    const items = res.data?.items || []

    videos.value = items.map((item) => ({
      videoId: item.id?.videoId,
      title: item.snippet?.title || "",
      channelTitle: item.snippet?.channelTitle || "",
      thumbnail: item.snippet?.thumbnails?.medium?.url
        || item.snippet?.thumbnails?.default?.url
        || "",
    })).filter(v => v.videoId)
  } catch (e) {
    errorMsg.value = "검색 중 오류가 발생하였습니다."
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.search-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  align-self: stretch;
  min-width: 56px;
  padding: 0 18px;
  line-height: 1.2;
  white-space: nowrap;
}
</style>
