import { defineStore } from "pinia"
import http from "@/api/http"

export const useAuthStore = defineStore("auth", {
  state: () => ({
    // 새로고침해도 username 유지
    user: JSON.parse(localStorage.getItem("user") || "null"),

    access: localStorage.getItem("access") || "",
    refresh: localStorage.getItem("refresh") || "",
  }),

  getters: {
    isLoggedIn: (state) => !!state.access,

    isLogin: (state) => !!state.access,
    token: (state) => state.access,
    username: (state) => state.user?.username || "",
  },

  actions: {
    async login(username, password) {
      const res = await http.post("/api/token/", { username, password })

      this.access = res.data.access
      this.refresh = res.data.refresh

      localStorage.setItem("access", this.access)
      localStorage.setItem("refresh", this.refresh)

      // username 저장 + 새로고침 대비
      this.user = { username }
      localStorage.setItem("user", JSON.stringify(this.user))
    },

    logout() {
      this.user = null
      this.access = ""
      this.refresh = ""

      localStorage.removeItem("access")
      localStorage.removeItem("refresh")
      localStorage.removeItem("user")
    },
  },
})