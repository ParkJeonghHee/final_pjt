<template>
  <div class="chatbot-overlay" ref="overlayRef">
    <!-- 💬 버튼 -->
    <button
      ref="fabRef"
      class="chatbot-fab"
      :style="fabStyle"
      @click="toggle"
      aria-label="Open chat"
    >
      💬
    </button>

    <!-- 창 -->
    <div
      ref="windowRef"
      class="chatbot-window"
      :class="{
        'is-open': isVisible && !closing,
        'is-closing': isVisible && closing,
      }"
      :style="windowStyle"
      v-show="isVisible"
      @mousedown.stop
      @animationend="onAnimEnd"
    >
      <!-- 헤더(드래그) -->
      <div class="chatbot-header" @mousedown.prevent="startDrag">
        <div class="fw-bold">Bankbook 챗봇</div>

        <div class="header-actions">
          <button class="btn-reset" @click.stop="onReset" title="채팅 초기화">
            초기화
          </button>
          <button class="btn-close" @click.stop="closeWithAnim" title="닫기">
            ×
          </button>
        </div>
      </div>

      <!-- 메시지 -->
      <div ref="scrollRef" class="chatbot-body">
        <div
          v-for="(m, idx) in messages"
          :key="idx"
          class="bubble-row"
          :class="m.role === 'user' ? 'right' : 'left'"
        >
          <!-- 🤖 봇 아바타: assistant만 -->
          <div v-if="m.role === 'assistant'" class="bot-avatar">🤖</div>

          <div class="bubble" :class="m.role === 'user' ? 'user' : 'bot'">
            <!-- ✅ 로딩 중: 말풍선 안 점점점 -->
            <span v-if="m.loading" class="typing-dots" aria-label="typing">
              <span>.</span><span>.</span><span>.</span>
            </span>

            <!-- ✅ 일반 메시지 -->
            <span v-else>{{ m.content }}</span>
          </div>
        </div>
      </div>

      <!-- 입력 -->
      <div class="chatbot-footer">
        <textarea
          ref="inputRef"
          class="form-control chatbot-input"
          v-model="input"
          placeholder="메시지를 입력하세요..."
          :disabled="loading"
          rows="1"
          @input="autoResizeInputAndWindow"
          @keydown.enter.exact.prevent="send"
          @keydown.enter.shift.stop
        ></textarea>

        <button
          class="btn btn-primary chatbot-send-btn"
          @click="send"
          :disabled="loading || !input.trim()"
        >
          전송
        </button>
      </div>

      <!-- 리사이즈 8방향 -->
      <div class="resize-handle top"    @mousedown.prevent.stop="startResize('top', $event)"></div>
      <div class="resize-handle right"  @mousedown.prevent.stop="startResize('right', $event)"></div>
      <div class="resize-handle bottom" @mousedown.prevent.stop="startResize('bottom', $event)"></div>
      <div class="resize-handle left"   @mousedown.prevent.stop="startResize('left', $event)"></div>

      <div class="resize-handle tl" @mousedown.prevent.stop="startResize('tl', $event)"></div>
      <div class="resize-handle tr" @mousedown.prevent.stop="startResize('tr', $event)"></div>
      <div class="resize-handle bl" @mousedown.prevent.stop="startResize('bl', $event)"></div>
      <div class="resize-handle br" @mousedown.prevent.stop="startResize('br', $event)"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onBeforeUnmount, onMounted, watch } from "vue"
import { useRoute } from "vue-router"
import { useAuthStore } from "@/stores/auth"
import { sendChat, fetchChatHistory, resetChatHistory } from "@/api/chat"

const overlayRef = ref(null)
const fabRef = ref(null)
const windowRef = ref(null)
const scrollRef = ref(null)
const inputRef = ref(null)

const auth = useAuthStore()
const route = useRoute()

const isVisible = ref(false)
const closing = ref(false)
const input = ref("")
const loading = ref(false)

const DEFAULT_GREETING = "안녕하세요! 어떤 상품을 추천받고 싶으신가요? (예: 안정적인 예금)"

const messages = ref([
  { role: "assistant", content: DEFAULT_GREETING, loading: false },
])

const fab = ref({ right: 18, bottom: 18 })
const pos = ref({ left: 0, top: 0 })
const size = ref({ width: 360, height: 520 })

const MIN_W = 300
const MAX_W = 900
const MIN_H = 380
const MAX_H = 900

// ✅ 입력이 길어질수록 창도 같이 늘리기 위한 값들
const INPUT_MAX_PX = 140          // textarea 최대 높이(이 이상은 textarea 내부 스크롤)
const inputBaseH = ref(38)        // 열었을 때 textarea 기본 높이
const winBaseH = ref(0)           // 열었을 때 창 기본 높이(1회 저장)

function clamp(v, min, max) {
  return Math.max(min, Math.min(max, v))
}

function initWindowPos() {
  const w = size.value.width
  const h = size.value.height
  const left = window.innerWidth - w - 18
  const top = window.innerHeight - h - 90
  pos.value.left = clamp(left, 8, window.innerWidth - w - 8)
  pos.value.top = clamp(top, 8, window.innerHeight - h - 8)
}

const fabStyle = computed(() => ({
  position: "fixed",
  right: fab.value.right + "px",
  bottom: fab.value.bottom + "px",
  zIndex: 2147483647,
}))

const windowStyle = computed(() => {
  const fabEl = fabRef.value
  const origin = fabEl ? fabEl.getBoundingClientRect() : null
  const ox = origin ? origin.left + origin.width / 2 : window.innerWidth - 30
  const oy = origin ? origin.top + origin.height / 2 : window.innerHeight - 30

  return {
    position: "fixed",
    left: pos.value.left + "px",
    top: pos.value.top + "px",
    width: size.value.width + "px",
    height: size.value.height + "px",
    zIndex: 2147483647,
    transformOrigin: `${ox}px ${oy}px`,
  }
})

// ✅ textarea 높이 자동 + 채팅창 높이 동기 증가
function autoResizeInputAndWindow() {
  const ta = inputRef.value
  if (!ta) return

  // textarea 높이 재계산
  ta.style.height = "auto"
  const nextH = Math.min(ta.scrollHeight, INPUT_MAX_PX)

  ta.style.height = nextH + "px"
  ta.style.overflowY = ta.scrollHeight > INPUT_MAX_PX ? "auto" : "hidden"

  // 창도 textarea 증가량만큼 같이 늘리기 (아래로 늘어나도록 height만 증가)
  const grow = Math.max(0, nextH - inputBaseH.value)
  const nextWinH = clamp(winBaseH.value + grow, MIN_H, MAX_H)

  size.value.height = nextWinH

  // 화면 밖으로 나가면 top 보정
  pos.value.top = clamp(pos.value.top, 0, window.innerHeight - size.value.height)
}

function scrollToBottom() {
  const el = scrollRef.value
  if (!el) return
  el.scrollTop = el.scrollHeight
}

async function loadHistoryOrGreeting() {
  // 로그인 상태면 DB에 저장된 채팅을 불러와서 이어하기
  if (auth.isLoggedIn) {
    try {
      const data = await fetchChatHistory()
      const hist = data?.history || []

      if (hist.length > 0) {
        messages.value = hist.map((h) => ({
          role: h.role,
          content: h.content,
          loading: false,
        }))
        return
      }
    } catch (e) {
      // 실패 시 아래 기본 인사로 fallback
    }
  }

  // 로그인 안 됐거나, history가 없거나, 실패 시 기본 인사
  messages.value = [{ role: "assistant", content: DEFAULT_GREETING, loading: false }]
}

async function openChat() {
  if (pos.value.left === 0 && pos.value.top === 0) initWindowPos()
  closing.value = false
  isVisible.value = true

  // ✅ 열자마자 계정별 히스토리 로드
  await loadHistoryOrGreeting()

  await nextTick(() => {
    scrollToBottom()

    // ✅ 기준값 저장 (처음 열 때만 winBaseH 저장)
    if (!winBaseH.value) winBaseH.value = size.value.height
    inputBaseH.value = inputRef.value?.offsetHeight || 38

    autoResizeInputAndWindow()
    inputRef.value?.focus()
  })
}

function closeWithAnim() {
  if (!isVisible.value) return
  closing.value = true
}

function toggle() {
  if (!isVisible.value) openChat()
  else closeWithAnim()
}

function onAnimEnd() {
  if (closing.value) {
    isVisible.value = false
    closing.value = false
  }
}

// ✅ 페이지 이동하면 닫기
watch(
  () => route.fullPath,
  () => {
    if (isVisible.value) closeWithAnim()
  }
)

// ✅ 탭 전환(visibility hidden)하면 닫기
function onVisibilityChange() {
  if (document.visibilityState === "hidden" && isVisible.value) {
    closeWithAnim()
  }
}

// ✅ 바깥 클릭하면 닫기
function onGlobalPointerDown(e) {
  if (!isVisible.value) return

  const w = windowRef.value
  const f = fabRef.value
  const target = e.target

  if (w && w.contains(target)) return
  if (f && f.contains(target)) return

  closeWithAnim()
}

onMounted(() => {
  document.addEventListener("visibilitychange", onVisibilityChange)
  window.addEventListener("pointerdown", onGlobalPointerDown, { capture: true })
})

onBeforeUnmount(() => {
  document.removeEventListener("visibilitychange", onVisibilityChange)
  window.removeEventListener("pointerdown", onGlobalPointerDown, { capture: true })
})

// ✅ 입력 변화 때마다(붙여넣기/자동완성 포함) 즉시 반영
watch(input, async () => {
  await nextTick()
  autoResizeInputAndWindow()
})

async function onReset() {
  // 로딩 중이면 막기
  if (loading.value) return

  // 로그인 상태면 DB에서도 삭제
  if (auth.isLoggedIn) {
    try {
      await resetChatHistory()
    } catch (e) {
      // reset 실패해도 화면은 초기화(UX)
    }
  }

  messages.value = [{ role: "assistant", content: DEFAULT_GREETING, loading: false }]
  input.value = ""
  await nextTick()
  autoResizeInputAndWindow()
  scrollToBottom()
  inputRef.value?.focus()
}

async function send() {
  const text = input.value.trim()
  if (!text || loading.value) return

  // 1) user 메시지
  messages.value.push({ role: "user", content: text, loading: false })
  input.value = ""
  await nextTick()
  autoResizeInputAndWindow()

  // 2) assistant 로딩 말풍선(점점점)
  const botPlaceholder = { role: "assistant", content: "", loading: true }
  messages.value.push(botPlaceholder)

  loading.value = true
  await nextTick(scrollToBottom)

  try {
    const data = await sendChat(text)
    const reply = (data?.reply || "응답을 받지 못했습니다.").trim()

    // ✅ 로딩 placeholder를 실제 답변으로 교체
    botPlaceholder.loading = false
    botPlaceholder.content = reply
  } catch (e) {
    botPlaceholder.loading = false
    botPlaceholder.content = "요청에 실패했습니다. 로그인/토큰 또는 서버 상태를 확인해주세요."
  } finally {
    loading.value = false
    await nextTick()
    autoResizeInputAndWindow()
    scrollToBottom()
    inputRef.value?.focus()
  }
}

let dragging = false
let dragStart = { x: 0, y: 0, left: 0, top: 0 }

function startDrag(e) {
  dragging = true
  dragStart = { x: e.clientX, y: e.clientY, left: pos.value.left, top: pos.value.top }
  attachWindowEvents()
}

let resizing = false
let resizeDir = null
let resizeStart = { x: 0, y: 0, left: 0, top: 0, w: 0, h: 0 }

function startResize(dir, e) {
  resizing = true
  resizeDir = dir
  resizeStart = {
    x: e.clientX,
    y: e.clientY,
    left: pos.value.left,
    top: pos.value.top,
    w: size.value.width,
    h: size.value.height,
  }
  attachWindowEvents()
}

function onMouseMove(e) {
  if (dragging) {
    const dx = e.clientX - dragStart.x
    const dy = e.clientY - dragStart.y
    let newLeft = dragStart.left + dx
    let newTop = dragStart.top + dy
    newLeft = clamp(newLeft, 0, window.innerWidth - size.value.width)
    newTop = clamp(newTop, 0, window.innerHeight - size.value.height)
    pos.value.left = newLeft
    pos.value.top = newTop
  }

  if (resizing) {
    const dx = e.clientX - resizeStart.x
    const dy = e.clientY - resizeStart.y

    let newLeft = resizeStart.left
    let newTop = resizeStart.top
    let newW = resizeStart.w
    let newH = resizeStart.h

    const isLeft = ["left", "tl", "bl"].includes(resizeDir)
    const isRight = ["right", "tr", "br"].includes(resizeDir)
    const isTop = ["top", "tl", "tr"].includes(resizeDir)
    const isBottom = ["bottom", "bl", "br"].includes(resizeDir)

    if (isRight) newW = resizeStart.w + dx
    if (isBottom) newH = resizeStart.h + dy
    if (isLeft) {
      newW = resizeStart.w - dx
      newLeft = resizeStart.left + dx
    }
    if (isTop) {
      newH = resizeStart.h - dy
      newTop = resizeStart.top + dy
    }

    const clampedW = clamp(newW, MIN_W, MAX_W)
    const clampedH = clamp(newH, MIN_H, MAX_H)

    if (isLeft && clampedW !== newW) newLeft -= (clampedW - newW)
    if (isTop && clampedH !== newH) newTop -= (clampedH - newH)

    newLeft = clamp(newLeft, 0, window.innerWidth - clampedW)
    newTop = clamp(newTop, 0, window.innerHeight - clampedH)

    size.value.width = clampedW
    size.value.height = clampedH
    pos.value.left = newLeft
    pos.value.top = newTop

    // ✅ 사용자가 리사이즈로 높이를 바꿨으면, 그 값을 기준으로 다시 잡기
    if (isVisible.value && !closing.value) {
      winBaseH.value =
        size.value.height -
        Math.max(0, (inputRef.value?.offsetHeight || 38) - inputBaseH.value)
    }
  }
}

function onMouseUp() {
  dragging = false
  resizing = false
  resizeDir = null
  detachWindowEvents()
}

function attachWindowEvents() {
  window.addEventListener("mousemove", onMouseMove)
  window.addEventListener("mouseup", onMouseUp)
}
function detachWindowEvents() {
  window.removeEventListener("mousemove", onMouseMove)
  window.removeEventListener("mouseup", onMouseUp)
}

onBeforeUnmount(() => {
  detachWindowEvents()
})
</script>

<style scoped>
.chatbot-overlay {
  position: fixed;
  inset: 0;
  z-index: 2147483647;
  pointer-events: none;
}

.chatbot-fab {
  pointer-events: auto;
  width: 68px;
  height: 68px;
  border-radius: 999px;
  border: none;
  background: #0d6efd;
  color: #fff;
  font-size: 30px;
  box-shadow: 0 8px 20px rgba(0,0,0,0.2);
}

.chatbot-window {
  pointer-events: auto;
  background: #fff;
  border: 1px solid #e9ecef;
  border-radius: 14px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.18);
  display: flex;
  flex-direction: column;
  overflow: hidden;

  opacity: 0;
  transform: scale(0.7);
  filter: blur(2px);
}

.chatbot-window.is-open {
  animation: popIn 220ms ease-out forwards;
}
.chatbot-window.is-closing {
  animation: suckIn 260ms cubic-bezier(.2,.8,.2,1) forwards;
}

@keyframes popIn {
  from { opacity: 0; transform: scale(0.7); filter: blur(2px); }
  to   { opacity: 1; transform: scale(1);   filter: blur(0px); }
}
@keyframes suckIn {
  0%   { opacity: 1; transform: scale(1);    filter: blur(0px); }
  100% { opacity: 0; transform: scale(0.15); filter: blur(2px); }
}

.chatbot-header {
  padding: 10px 12px;
  border-bottom: 1px solid #f1f3f5;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #f8f9fa;
  cursor: move;
  user-select: none;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

/* 초기화 버튼 */
.btn-reset {
  border: 1px solid #dee2e6;
  background: #fff;
  color: #495057;
  border-radius: 8px;
  padding: 6px 10px;
  font-size: 13px;
  line-height: 1;
  cursor: pointer;
}
.btn-reset:hover {
  background: #f1f3f5;
}

/* 닫기 */
.btn-close {
  border: none;
  background: transparent;
  font-size: 22px;
  line-height: 1;
  cursor: pointer;
  color: #495057;
}

.chatbot-body {
  flex: 1;
  padding: 12px;
  overflow-y: auto;
  overflow-x: hidden;
  background: #ffffff;
}

.bubble-row { display: flex; align-items: flex-end; margin-bottom: 10px; gap: 8px; }
.bubble-row.left { justify-content: flex-start; }
.bubble-row.right { justify-content: flex-end; }

/* 🤖 봇 아바타 */
.bot-avatar {
  font-size: 28px;
  line-height: 1;
  flex: 0 0 auto;
  margin-bottom: 2px;
}

.bubble {
  max-width: 78%;
  padding: 10px 12px;
  border-radius: 14px;
  font-size: 14px;
  line-height: 1.35;
  white-space: pre-wrap;
  word-break: break-word;
  overflow-wrap: break-word;
}
.bubble.bot { background: #f1f3f5; color: #212529; border-top-left-radius: 6px; }
.bubble.user { background: #0d6efd; color: #fff; border-top-right-radius: 6px; }

.chatbot-footer {
  padding: 10px;
  border-top: 1px solid #f1f3f5;
  display: flex;
  gap: 8px;
  align-items: flex-end;
}

/* ===== 말풍선 꼬리 ===== */

/* 봇 말풍선 꼬리 (왼쪽, 🤖에서 나오는 느낌) */
.bubble.bot {
  position: relative;
}
.bubble.bot::before {
  content: "";
  position: absolute;
  left: -8px;
  bottom: 10px;
  width: 0;
  height: 0;
  border-top: 8px solid transparent;
  border-bottom: 8px solid transparent;
  border-right: 8px solid #f1f3f5; /* 봇 말풍선 색 */
}

/* 사용자 말풍선 꼬리 (오른쪽) */
.bubble.user {
  position: relative;
}
.bubble.user::after {
  content: "";
  position: absolute;
  right: -8px;
  bottom: 10px;
  width: 0;
  height: 0;
  border-top: 8px solid transparent;
  border-bottom: 8px solid transparent;
  border-left: 8px solid #0d6efd; /* 사용자 말풍선 색 */
}

/* ✅ 입력 늘어나면 textarea도 커지고, 너무 커지면 textarea 내부 스크롤 */
.chatbot-input {
  flex: 1;
  min-height: 38px;
  max-height: 140px; /* INPUT_MAX_PX와 일치 */
  resize: none;
  white-space: pre-wrap;
  word-break: break-word;
  overflow-y: auto;
}

.chatbot-send-btn {
  flex: 0 0 auto;
  min-width: 64px;
  padding: 8px 12px;

  white-space: nowrap;
  word-break: keep-all;
  writing-mode: horizontal-tb;

  display: flex;
  align-items: center;
  justify-content: center;
}

.typing-dots {
  display: inline-flex;
  gap: 4px;
  font-size: 22px;
  line-height: 1;
  align-items: baseline;
}
.typing-dots span {
  animation: blink 1.4s infinite both;
}
.typing-dots span:nth-child(2) { animation-delay: 0.2s; }
.typing-dots span:nth-child(3) { animation-delay: 0.4s; }

@keyframes blink {
  0% { opacity: 0.2; }
  20% { opacity: 1; }
  100% { opacity: 0.2; }
}

.resize-handle { position: absolute; z-index: 2147483647; }
.resize-handle.top    { left: 10px; right: 10px; top: 0; height: 8px; cursor: ns-resize; }
.resize-handle.bottom { left: 10px; right: 10px; bottom: 0; height: 8px; cursor: ns-resize; }
.resize-handle.left   { top: 10px; bottom: 10px; left: 0; width: 8px; cursor: ew-resize; }
.resize-handle.right  { top: 10px; bottom: 10px; right: 0; width: 8px; cursor: ew-resize; }

.resize-handle.tl { top: 0; left: 0; width: 14px; height: 14px; cursor: nwse-resize; }
.resize-handle.tr { top: 0; right: 0; width: 14px; height: 14px; cursor: nesw-resize; }
.resize-handle.bl { bottom: 0; left: 0; width: 14px; height: 14px; cursor: nesw-resize; }
.resize-handle.br { bottom: 0; right: 0; width: 14px; height: 14px; cursor: nwse-resize; }
</style>
