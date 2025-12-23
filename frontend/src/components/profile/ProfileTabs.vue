<template>
  <div class="border-bottom mb-3 pb-2">
    <a
      href="#"
      class="text-decoration-none tab-link"
      :class="modelValue === 'info' ? 'fw-bold text-dark' : 'text-muted'"
      @click.prevent="$emit('update:modelValue', 'info')"
    >
      기본 정보 수정
    </a>
    <span class="divider"> | </span>

    <a
      href="#"
      class="text-decoration-none tab-link"
      :class="modelValue === 'portfolio' ? 'fw-bold text-dark' : 'text-muted'"
      @click.prevent="$emit('update:modelValue', 'portfolio')"
    >
      가입한 상품
    </a>
    <span class="divider"> | </span>

    <a
      href="#"
      class="text-decoration-none tab-link"
      :class="modelValue === 'recommend' ? 'fw-bold text-dark' : 'text-muted'"
      @click.prevent="$emit('update:modelValue', 'recommend')"
    >
      상품 추천 받기
    </a>
    <span class="divider"> | </span>

    <a
      href="#"
      class="text-decoration-none tab-link"
      :class="modelValue === 'videos' ? 'fw-bold text-dark' : 'text-muted'"
      @click.prevent="$emit('update:modelValue', 'videos')"
    >
      관심 동영상
    </a>
  </div>
</template>

<script setup>
defineProps({
  modelValue: { type: String, default: "info" },
})
defineEmits(["update:modelValue"])
</script>

<style scoped>
.divider {
  color: #adb5bd;
}
.tab-link {
  margin-right: 6px;
}
</style>
