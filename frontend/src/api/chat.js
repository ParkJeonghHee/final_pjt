import http from "@/api/http"

export async function sendChat(message) {
  const res = await http.post("/api/chat/", { message })
  return res.data
}

export async function fetchChatHistory() {
  const res = await http.get("/api/chat/history/")
  return res.data
}

export async function resetChatHistory() {
  const res = await http.post("/api/chat/reset/")
  return res.data
}
