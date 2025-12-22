<template>
  <main class="container my-5">
    <div class="p-4 border rounded bg-white">
      <h4 class="fw-bold mb-3">글 수정</h4>

      <p v-if="errorMsg" class="text-danger fw-semibold">{{ errorMsg }}</p>

      <div v-if="loading" class="text-muted">불러오는 중...</div>

      <div v-else>
        <div class="mb-3">
          <label class="form-label">제목</label>
          <input class="form-control" v-model="title" maxlength="200" />
        </div>

        <div class="mb-3">
          <label class="form-label">내용</label>
          <textarea class="form-control" rows="8" v-model="content"></textarea>
        </div>

        <div class="d-flex gap-2">
          <button
            class="btn btn-success"
            :disabled="saving"
            @click="onSave"
          >
            {{ saving ? "저장 중..." : "저장" }}
          </button>

          <RouterLink class="btn btn-outline-secondary" :to="`/community/${id}`">
            취소
          </RouterLink>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref, onMounted } from "vue"
import { useRoute, useRouter } from "vue-router"
import { fetchPostDetail, updatePost } from "@/api/community"

const route = useRoute()
const router = useRouter()

const id = route.params.id

const title = ref("")
const content = ref("")
const loading = ref(true)
const saving = ref(false)
const errorMsg = ref("")

async function loadDetail() {
  loading.value = true
  errorMsg.value = "" 

  try {
    const res = await fetchPostDetail(id)
    title.value = res.data?.title ?? ""
    content.value = res.data?.content ?? ""
  } catch (err) {
    errorMsg.value =
      err?.response?.data?.detail || "게시글 정보를 불러오지 못했습니다."
  } finally {
    loading.value = false
  }
}

async function onSave() {
  errorMsg.value = ""

  if (!title.value.trim() || !content.value.trim()) {
    errorMsg.value = "제목과 내용을 입력해주세요"
    return
  }

  saving.value = true
  try {
    await updatePost(id, {
      title: title.value,
      content: content.value,
    })

    router.push(`/community/${id}`)
  } catch (err) {
    errorMsg.value =
      err?.response?.data?.detail || "수정 권한이 없거나 수정에 실패하였습니다."
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadDetail()
})
</script>
