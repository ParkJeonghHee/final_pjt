<template>
  <main class="container my-4">
    <div class="p-4 border rounded bg-white mb-3">
      <h4 class="fw-bold mb-0">{{ auth.username }} 님의 프로필</h4>
    </div>

    <ProfileTabs v-model="tab" />

    <div class="p-4 border rounded bg-white">
      <ProfileInfoTab v-if="tab === 'info'" />
      <template v-else-if="tab === 'portfolio'">
        <h5 class="fw-bold">포트폴리오 수정</h5>
        <p class="text-muted mb-0">나중에 붙일 예정</p>
      </template>
      <ProfileRecommendTab v-else-if="tab === 'recommend'" />
      <ProfileVideosTab v-else-if="tab === 'videos'" />
    </div>
  </main>
</template>

<script setup>
import { ref } from "vue"
import { useAuthStore } from "@/stores/auth"

import ProfileTabs from "@/components/profile/ProfileTabs.vue"
import ProfileInfoTab from "@/components/profile/ProfileInfoTab.vue"
import ProfileRecommendTab from "@/components/profile/ProfileRecommendTab.vue"
import ProfileVideosTab from "@/components/profile/ProfileVideosTab.vue"

const auth = useAuthStore()
const tab = ref("info")
</script>
