import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
    state: () => ({
        isLoggedIn: false,
        username: null,
    }),
    actions: {
        login(username) {
            this.isLoggedIn = true
            this.username = username
        },
        logout() {
            this.isLoggedIn = false
            this.username = null
        },
    },
})