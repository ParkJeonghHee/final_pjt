import { defineStore } from "pinia"
import http from "@/api/http"

export const useAuthStore = defineStore("auth", {
  state: () => ({
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

      this.user = { username }
      localStorage.setItem("user", JSON.stringify(this.user))

      http.defaults.headers.common.Authorization = `Bearer ${this.access}`
    },

    logout() {
      this.user = null
      this.access = ""
      this.refresh = ""

      localStorage.removeItem("access")
      localStorage.removeItem("refresh")
      localStorage.removeItem("user")

      delete http.defaults.headers.common.Authorization

      window.location.reload()
    },
  },
})
