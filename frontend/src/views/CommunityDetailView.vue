<template>
  <main class="container my-5">
    <div class="p-4 border rounded bg-white">
      <!-- 게시글 헤더 -->
      <div class="d-flex justify-content-between align-items-start">
        <div>
          <h4 class="fw-bold mb-1">{{ post?.title }}</h4>
          <div class="text-muted small">
            작성자: {{ post?.author_username }} ·
            작성일: {{ formatDate(post?.created_at) }}
          </div>
        </div>

        <div class="d-flex gap-2" v-if="post">
          <RouterLink class="btn btn-outline-secondary" to="/community">
            목록
          </RouterLink>
          <RouterLink
            v-if="isOwner"
            class="btn btn-outline-success"
            :to="`/community/${id}/edit`"
          >
            수정
          </RouterLink>
          <button v-if="isOwner" class="btn btn-danger" @click="onDeletePost">
            삭제
          </button>
        </div>
      </div>

      <hr />

      <p v-if="errorMsg" class="text-danger fw-semibold">{{ errorMsg }}</p>
      <div v-if="loading" class="text-muted">불러오는 중...</div>

      <div v-else-if="post">
        <!-- 본문 -->
        <div class="mb-4" style="white-space: pre-wrap">
          {{ post.content }}
        </div>

        <!-- 댓글 헤더 -->
        <div class="d-flex justify-content-between align-items-center mt-4">
          <h5 class="fw-bold mb-0">
            댓글
            <span class="text-muted fs-6">
              (총 {{ post.comment_count }}개)
            </span>
          </h5>

          <!-- 댓글 정렬 -->
          <select
            class="form-select form-select-sm w-auto"
            v-model="sortOption"
            @change="loadDetail"
          >
            <option value="latest">최신순</option>
            <option value="oldest">오래된순</option>
            <option value="likes">좋아요순</option>
          </select>
        </div>

        <!-- 댓글 작성 -->
        <div class="border rounded p-3 mb-3 mt-3">
          <div class="mb-2 fw-semibold">댓글 작성</div>
          <textarea
            class="form-control mb-2"
            rows="3"
            v-model="newComment"
            placeholder="댓글을 입력하세요"
          ></textarea>
          <button
            class="btn btn-success"
            :disabled="commentLoading"
            @click="onCreateComment"
          >
            {{ commentLoading ? "등록 중..." : "등록" }}
          </button>
        </div>

        <!-- 댓글 리스트 -->
        <div v-if="comments.length === 0" class="text-muted">
          댓글이 없습니다.
        </div>

        <div v-else class="list-group">
          <div class="list-group-item" v-for="c in comments" :key="c.id">
            <div class="d-flex justify-content-between align-items-start">
              <div class="w-100">
                <div class="small text-muted mb-1">
                  {{ c.author_username }} · {{ formatDate(c.created_at) }}
                  <span
                    v-if="shouldShowCommentUpdated(c)"
                    class="ms-2"
                  >
                    (수정: {{ formatDate(c.updated_at) }})
                  </span>
                </div>

                <div v-if="editCommentId === c.id">
                  <textarea
                    class="form-control mb-2"
                    rows="2"
                    v-model="editCommentText"
                  ></textarea>
                  <div class="d-flex gap-2">
                    <button
                      class="btn btn-success btn-sm"
                      @click="onUpdateComment(c.id)"
                    >
                      저장
                    </button>
                    <button
                      class="btn btn-outline-secondary btn-sm"
                      @click="cancelEditComment"
                    >
                      취소
                    </button>
                  </div>
                </div>

                <div v-else style="white-space: pre-wrap">
                  {{ c.content }}
                </div>

                <!-- 좋아요 버튼 -->
                <button
                  class="btn btn-sm mt-2"
                  :class="c.is_liked ? 'btn-danger' : 'btn-outline-danger'"
                  @click="onToggleLike(c.id)"
                >
                  ❤️ {{ c.like_count }}
                </button>
              </div>

              <!-- 본인 댓글 -->
              <div class="ms-3" v-if="isMyComment(c)">
                <div class="d-flex gap-2">
                  <button
                    class="btn btn-outline-success btn-sm"
                    @click="startEditComment(c)"
                  >
                    수정
                  </button>
                  <button
                    class="btn btn-outline-danger btn-sm"
                    @click="onDeleteComment(c.id)"
                  >
                    삭제
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref, computed, onMounted } from "vue"
import { useRoute, useRouter } from "vue-router"
import { useAuthStore } from "@/stores/auth"
import {
  fetchPostDetail,
  deletePost,
  createComment,
  updateComment,
  deleteComment,
  toggleCommentLike,
} from "@/api/community"

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()
const id = route.params.id

const post = ref(null)
const comments = ref([])
const loading = ref(false)
const errorMsg = ref("")

const newComment = ref("")
const commentLoading = ref(false)

const editCommentId = ref(null)
const editCommentText = ref("")

const sortOption = ref("latest")

function getMyUsername() {
  return auth.user?.username || ""
}

function formatDate(iso) {
  if (!iso) return ""
  return new Date(iso).toLocaleString()
}

const isOwner = computed(() => {
  const me = getMyUsername()
  return me && post.value && post.value.author_username === me
})

function isMyComment(c) {
  const me = getMyUsername()
  return me && c.author_username === me
}

async function loadDetail() {
  loading.value = true
  errorMsg.value = ""
  try {
    const res = await fetchPostDetail(id, sortOption.value)
    post.value = res.data
    comments.value = res.data.comments || []
  } catch (err) {
    errorMsg.value =
      err?.response?.data?.detail || "게시글 정보를 불러오지 못했습니다."
  } finally {
    loading.value = false
  }
}

async function onDeletePost() {
  if (!confirm("정말 삭제할까요?")) return
  await deletePost(id)
  router.push("/community")
}

async function onCreateComment() {
  if (!newComment.value.trim()) return
  commentLoading.value = true
  await createComment(id, { content: newComment.value })
  newComment.value = ""
  await loadDetail()
  commentLoading.value = false
}

function startEditComment(c) {
  editCommentId.value = c.id
  editCommentText.value = c.content
}

function cancelEditComment() {
  editCommentId.value = null
  editCommentText.value = ""
}

async function onUpdateComment(commentId) {
  await updateComment(commentId, { content: editCommentText.value })
  cancelEditComment()
  await loadDetail()
}

async function onDeleteComment(commentId) {
  if (!confirm("댓글을 삭제할까요?")) return
  await deleteComment(commentId)
  await loadDetail()
}

async function onToggleLike(commentId) {
  await toggleCommentLike(commentId)
  await loadDetail()
}

function shouldShowCommentUpdated(comment) {
  if (!comment?.created_at || !comment?.updated_at) return false
  return new Date(comment.updated_at) > new Date(comment.created_at)
}

onMounted(loadDetail)
</script>
