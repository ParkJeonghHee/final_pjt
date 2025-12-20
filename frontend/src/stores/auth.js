import { defineStore } from "pinia"
import http from "@/api/http"

export const useAuthStore = defineStore("auth", {
  state: () => ({
    user: null,
    access: localStorage.getItem("access") || "",
    refresh: localStorage.getItem("refresh") || "",
  }),
  getters: {
    isLoggedIn: (state) => !!state.access,
  },
  actions: {
    async login(username, password) {
      const res = await http.post("/api/token/", { username, password })
      this.access = res.data.access
      this.refresh = res.data.refresh

      localStorage.setItem("access", this.access)
      localStorage.setItem("refresh", this.refresh)

      this.user = { username }
    },
    logout() {
      this.user = null
      this.access = ""
      this.refresh = ""
      localStorage.removeItem("access")
      localStorage.removeItem("refresh")
    },
  },
})
