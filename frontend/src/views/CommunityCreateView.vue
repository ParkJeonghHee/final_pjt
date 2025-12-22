<template>
  <main class="container my-5">
    <div class="p-4 border rounded bg-white">
      <h4 class="fw-bold mb-3">글 작성</h4>

      <p v-if="errorMsg" class="text-danger fw-semibold mb-3">
        {{ errorMsg }}
      </p>

      <div class="mb-3">
        <label class="form-label">제목</label>
        <input class="form-control" v-model="title" maxlength="200" />
      </div>

      <div class="mb-3">
        <label class="form-label">내용</label>
        <textarea
          class="form-control"
          rows="8"
          v-model="content"
          placeholder="내용을 입력하세요"
        ></textarea>
      </div>

      <div class="d-flex gap-2">
        <button class="btn btn-success" :disabled="loading" @click="onSubmit">
          {{ loading ? "등록 중..." : "등록" }}
        </button>
        <RouterLink class="btn btn-outline-secondary" to="/community">
          취소
        </RouterLink>
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref } from "vue"
import { useRouter } from "vue-router"
import { createPost } from "@/api/community"

const router = useRouter()

const title = ref("")
const content = ref("")
const loading = ref(false)
const errorMsg = ref("")

async function onSubmit() {
  errorMsg.value = ""

  if (!title.value.trim() || !content.value.trim()) {
    errorMsg.value = "제목과 내용을 모두 입력해주세요."
    return
  }

  loading.value = true
  try {
    const res = await createPost({ title: title.value, content: content.value })
    const newId = res?.data?.id
    router.push(newId ? `/community/${newId}` : "/community")
  } catch (err) {

    const detail = err?.response?.data?.detail
    const data = err?.response?.data
    errorMsg.value =
      detail ||
      (data && JSON.stringify(data)) ||
      "게시글 작성에 실패했습니다."
  } finally {
    loading.value = false
  }
}
</script>
