<template>
  <div>
    <h5 class="fw-bold">관심 동영상</h5>
    <p class="text-muted mb-3">저장한 관심 동영상 목록</p>

    <div v-if="videos.length === 0" class="text-muted">
      아직 저장된 동영상이 없습니다.
    </div>

    <ul v-else class="list-group">
      <li v-for="v in videos" :key="v.id" class="list-group-item">
        <div class="d-flex gap-3 align-items-start">
          <a :href="v.url" target="_blank" rel="noopener">
            <img
              :src="getThumb(v)"
              :alt="v.title"
              style="width: 160px; height: 90px; object-fit: cover; border-radius: 8px;"
            />
          </a>

          <div class="flex-grow-1">
            <div class="fw-semibold mb-1">{{ v.title }}</div>
            <div v-if="v.channelTitle" class="text-muted small">채널명: {{ v.channelTitle }}</div>
            <div v-if="v.publishedAt" class="text-muted small mb-2">업로드 날짜: {{ v.publishedAt }}</div>
            <a :href="v.url" target="_blank" rel="noopener" class="small">
              {{ v.url }}
            </a>
          </div>

          <button class="btn btn-outline-danger btn-sm" @click="removeVideo(v.id)">
            삭제
          </button>
        </div>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { computed } from "vue"
import { useSavedVideosStore } from "@/stores/savedVideos"

const savedStore = useSavedVideosStore()
const videos = computed(() => savedStore.list)

function removeVideo(id) {
  savedStore.remove(id)
}

function getThumb(v) {
  if (v.thumbnail) return v.thumbnail
  return `https://i.ytimg.com/vi/${v.id}/hqdefault.jpg`
}
</script>
