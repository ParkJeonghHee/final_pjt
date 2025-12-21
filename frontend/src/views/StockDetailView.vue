<template>
  <main class="container my-5">
    <div class="p-4 border rounded bg-white">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h4 class="fw-bold mb-0">영상 상세 페이지</h4>
        <button class="btn btn-outline-secondary" @click="goBack">뒤로</button>
      </div>

      <p v-if="errorMsg" class="text-danger fw-semibold mb-3">
        {{ errorMsg }}
      </p>

      <div v-if="loading" class="text-muted">불러오는 중...</div>

      <div v-else-if="video">
        <h5 class="fw-bold mb-2">{{ video.title }}</h5>
        <div class="text-muted mb-1">채널명: {{ video.channelTitle }}</div>
        <div class="text-muted mb-3">업로드 날짜: {{ video.publishedAt }}</div>

        <div class="ratio ratio-16x9 mb-3">
          <iframe
            :src="embedUrl"
            title="YouTube video player"
            frameborder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
            allowfullscreen
          ></iframe>
        </div>

        <p class="mb-0" style="white-space: pre-line;">
          {{ video.description }}
        </p>
      </div>
    </div>
  </main>
</template>

<script setup>
import { computed, onMounted, ref } from "vue"
import { useRoute, useRouter } from "vue-router"
import { fetchYoutubeVideoDetail } from "@/api/youtube"

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const errorMsg = ref("")
const video = ref(null)

const videoId = computed(() => route.params.videoId)

const embedUrl = computed(() => {
  return `https://www.youtube.com/embed/${videoId.value}`
})

function goBack() {
  router.back()
}

onMounted(async () => {
  loading.value = true
  errorMsg.value = ""
  try {
    const res = await fetchYoutubeVideoDetail(videoId.value)
    const item = res.data?.items?.[0]
    if (!item) {
      errorMsg.value = "선택된 조건에 해당하는 데이터가 없습니다."
      video.value = null
      return
    }

    video.value = {
      title: item.snippet?.title || "",
      channelTitle: item.snippet?.channelTitle || "",
      publishedAt: (item.snippet?.publishedAt || "").slice(0, 10),
      description: item.snippet?.description || "",
    }
  } catch (e) {
    errorMsg.value = "데이터를 불러오는 중 오류가 발생하였습니다."
    video.value = null
  } finally {
    loading.value = false
  }
})
</script>
