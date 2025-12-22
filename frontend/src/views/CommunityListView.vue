<template>
  <main class="container my-5">
    <div class="p-4 border rounded bg-white">
      <!-- 제목 + 정렬 + 글 작성 버튼 -->
      <div class="d-flex justify-content-between align-items-center mb-3">
        <div class="d-flex align-items-center gap-3">
          <h4 class="fw-bold mb-0">
            커뮤니티
            <span class="text-muted fs-6">
              (총 {{ totalCount }}개)
            </span>
          </h4>

          <!-- 게시글 정렬 -->
          <select
            class="form-select form-select-sm w-auto"
            v-model="sortOption"
            @change="loadPosts"
          >
            <option value="latest">최신순</option>
            <option value="oldest">오래된순</option>
            <option value="likes">좋아요순</option>
          </select>
        </div>

        <RouterLink class="btn btn-success" to="/community/create">
          글 작성
        </RouterLink>
      </div>

      <!-- 에러 메시지 -->
      <p v-if="errorMsg" class="text-danger fw-semibold">
        {{ errorMsg }}
      </p>

      <!-- 로딩 -->
      <div v-if="loading" class="text-muted">
        불러오는 중...
      </div>

      <!-- 게시글 목록 -->
      <div v-else>
        <div v-if="posts.length === 0" class="text-muted">
          게시글이 없습니다.
        </div>

        <table v-else class="table align-middle">
          <thead>
            <tr>
              <th style="width: 80px">번호</th>
              <th>제목</th>
              <th style="width: 140px">좋아요</th>
              <th style="width: 180px">작성자</th>
              <th style="width: 220px">작성일</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="(p, index) in posts" :key="p.id">
              <td>{{ totalCount - index }}</td>

              <td>
                <RouterLink :to="`/community/${p.id}`">
                  {{ p.title }}
                </RouterLink>
              </td>

              <td>
                <button
                    type="button"
                    class="btn btn-sm"
                    :class="p.is_liked ? 'btn-danger' : 'btn-outline-danger'"
                    :disabled="likeLoadingId === p.id"
                    @click.stop.prevent="onTogglePostLike(p.id)"
                >
                    ❤️ {{ p.like_count ?? 0 }}
                </button>

              </td>

              <td>{{ p.author_username }}</td>

              <td>
                {{ formatDate(p.created_at) }}
                <span
                  v-if="shouldShowUpdated(p)"
                  class="text-muted ms-2"
                >
                  (수정: {{ formatDate(p.updated_at) }})
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref, onMounted } from "vue"
import { fetchPosts, togglePostLike } from "@/api/community"
import { useAuthStore } from "@/stores/auth"

const auth = useAuthStore()

const posts = ref([])
const totalCount = ref(0)
const errorMsg = ref("")
const loading = ref(false)

const sortOption = ref("latest") 
const likeLoadingId = ref(null)

async function loadPosts() {
  errorMsg.value = ""
  loading.value = true

  try {
    const res = await fetchPosts(sortOption.value)
    posts.value = res.data.results
    totalCount.value = res.data.count
  } catch (err) {
    const detail = err?.response?.data?.detail
    errorMsg.value = detail || "게시글 목록을 불러오지 못했습니다."
  } finally {
    loading.value = false
  }
}


async function onTogglePostLike(postId) {
  errorMsg.value = ""
  likeLoadingId.value = postId

  try {
    await togglePostLike(postId)
    await loadPosts()
  } catch (err) {
    const detail = err?.response?.data?.detail
    errorMsg.value = detail || "좋아요 처리에 실패했습니다."
  } finally {
    likeLoadingId.value = null
  }
}

function formatDate(dateStr) {
  if (!dateStr) return ""
  const d = new Date(dateStr)
  if (Number.isNaN(d.getTime())) return dateStr
  return d.toLocaleDateString("ko-KR", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  })
}


function shouldShowUpdated(post) {
  if (!post?.created_at || !post?.updated_at) return false

  const created = new Date(post.created_at)
  const updated = new Date(post.updated_at)

  if (Number.isNaN(created.getTime()) || Number.isNaN(updated.getTime())) {
    return false
  }

  return updated.getTime() > created.getTime()
}

onMounted(() => {
  loadPosts()
})
</script>
