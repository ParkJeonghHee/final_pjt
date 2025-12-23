<template>
  <main class="container my-4">
    <div class="p-4 border rounded bg-white mb-3">
      <h4 class="fw-bold mb-0">{{ auth.username }} 님의 프로필</h4>
    </div>

    <ProfileTabs v-model="tab" />

    <div class="p-4 border rounded bg-white">
      <ProfileInfoTab v-if="tab === 'info'" />
      <ProfilePortfolioTab v-else-if="tab === 'portfolio'" />
      <ProfileRecommendTab v-else-if="tab === 'recommend'" />
      <ProfileVideosTab v-else-if="tab === 'videos'" />
    </div>
  </main>
</template>

<script setup>
import { ref, watchEffect } from "vue"
import { useRoute } from "vue-router"
import { useAuthStore } from "@/stores/auth"

import ProfileTabs from "@/components/profile/ProfileTabs.vue"
import ProfileInfoTab from "@/components/profile/ProfileInfoTab.vue"
import ProfilePortfolioTab from "@/components/profile/ProfilePortfolioTab.vue"
import ProfileRecommendTab from "@/components/profile/ProfileRecommendTab.vue"
import ProfileVideosTab from "@/components/profile/ProfileVideosTab.vue"

const auth = useAuthStore()
const route = useRoute()

const tab = ref("info")

watchEffect(() => {
  const q = route.query.tab
  const next = Array.isArray(q) ? q[0] : q
  tab.value = next || "info"
})
</script>

