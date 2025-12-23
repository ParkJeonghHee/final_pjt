<template>
  <div>
    <h5 class="fw-bold mb-3">기본 정보 수정</h5>

    <div v-if="loading" class="text-muted">불러오는 중...</div>

    <div v-else>
      <p v-if="errorMsg" class="text-danger fw-semibold mb-3">
        {{ errorMsg }}
      </p>

      <p v-if="successMsg" class="text-success fw-semibold mb-3">
        {{ successMsg }}
      </p>

      <div class="mb-3">
        <label class="form-label">회원번호</label>
        <input class="form-control" :value="profile.id ?? ''" disabled />
      </div>

      <div class="mb-3">
        <label class="form-label">ID</label>
        <input class="form-control" :value="profile.username ?? ''" disabled />
      </div>

      <div class="mb-3 d-flex gap-2 align-items-end">
        <div class="flex-grow-1">
          <label class="form-label">Email</label>
          <input
            class="form-control"
            v-model="profile.email"
            placeholder="이메일을 설정해주세요"
          />
        </div>
        <button
          class="btn btn-primary"
          :disabled="savingField !== null"
          @click="onSaveField('email')"
        >
          {{ savingField === "email" ? "수정 중..." : "수정하기" }}
        </button>
      </div>

      <div class="mb-3 d-flex gap-2 align-items-end">
        <div class="flex-grow-1">
          <label class="form-label">Nickname</label>
          <input
            class="form-control"
            v-model="profile.nickname"
            placeholder="닉네임을 설정해주세요"
          />
        </div>
        <button
          class="btn btn-primary"
          :disabled="savingField !== null"
          @click="onSaveField('nickname')"
        >
          {{ savingField === "nickname" ? "수정 중..." : "수정하기" }}
        </button>
      </div>

      <div class="mb-3 d-flex gap-2 align-items-end">
        <div class="flex-grow-1">
          <label class="form-label">나이</label>
          <input
            class="form-control"
            v-model.number="profile.age"
            type="number"
            min="0"
          />
        </div>
        <button
          class="btn btn-primary"
          :disabled="savingField !== null"
          @click="onSaveField('age')"
        >
          {{ savingField === "age" ? "수정 중..." : "수정하기" }}
        </button>
      </div>

      <div class="mb-3 d-flex gap-2 align-items-end">
        <div class="flex-grow-1">
          <label class="form-label">총 자산</label>
          <input
            class="form-control"
            v-model.number="profile.total_assets"
            type="number"
            min="0"
          />
        </div>
        <button
          class="btn btn-primary"
          :disabled="savingField !== null"
          @click="onSaveField('total_assets')"
        >
          {{ savingField === "total_assets" ? "수정 중..." : "수정하기" }}
        </button>
      </div>

      <div class="mb-3 d-flex gap-2 align-items-end">
        <div class="flex-grow-1">
          <label class="form-label">월 소득</label>
          <input
            class="form-control"
            v-model.number="profile.income"
            type="number"
            min="0"
          />
        </div>
        <button
          class="btn btn-primary"
          :disabled="savingField !== null"
          @click="onSaveField('income')"
        >
          {{ savingField === "income" ? "수정 중..." : "수정하기" }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import http from "@/api/http"

const profile = ref({
  id: null,
  username: "",
  email: "",
  nickname: "",
  age: null,
  total_assets: null,
  income: null,
})

const loading = ref(false)
const savingField = ref(null)
const errorMsg = ref("")
const successMsg = ref("")

async function loadProfile() {
  loading.value = true
  errorMsg.value = ""
  successMsg.value = ""

  try {
    const res = await http.get("/api/accounts/profile/")
    profile.value = res.data
  } catch (err) {
    errorMsg.value = "프로필 정보를 불러오지 못했습니다."
  } finally {
    loading.value = false
  }
}

async function onSaveField(field) {
  if (savingField.value !== null) return

  savingField.value = field
  errorMsg.value = ""
  successMsg.value = ""

  try {
    const payload = { [field]: profile.value[field] }
    const res = await http.patch("/api/accounts/profile/", payload)
    profile.value = res.data
    successMsg.value = "수정이 완료되었습니다."
  } catch (err) {
    const data = err?.response?.data
    errorMsg.value =
      data?.detail ||
      (Array.isArray(data?.[field]) ? data[field][0] : null) ||
      "수정에 실패했습니다."
  } finally {
    savingField.value = null
  }
}

onMounted(() => {
  loadProfile()
})
</script>
