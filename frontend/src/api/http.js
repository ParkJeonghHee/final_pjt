import axios from "axios"

const BASE_URL = "http://127.0.0.1:8000"

const http = axios.create({
  baseURL: BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
})

http.interceptors.request.use(
  (config) => {
    const access = localStorage.getItem("access")

    if (access) {
      config.headers.Authorization = `Bearer ${access}`
    } else {
      delete config.headers.Authorization
    }

    return config
  },
  (error) => Promise.reject(error)
)


let isRefreshing = false
let refreshQueue = []

function resolveQueue(error, newAccess = null) {
  refreshQueue.forEach((p) => {
    if (error) p.reject(error)
    else p.resolve(newAccess)
  })
  refreshQueue = []
}

http.interceptors.response.use(
  (response) => response,
  async (error) => {
    const status = error?.response?.status
    const originalRequest = error?.config

    if (status !== 401) return Promise.reject(error)

    const isRefreshCall = originalRequest?.url?.includes("/api/token/refresh/")
    if (isRefreshCall) {
      localStorage.removeItem("access")
      localStorage.removeItem("refresh")
      return Promise.reject(error)
    }

    if (originalRequest?._retry) return Promise.reject(error)
    originalRequest._retry = true

    const refresh = localStorage.getItem("refresh")
    if (!refresh) {
      return Promise.reject(error)
    }

    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        refreshQueue.push({ resolve, reject })
      }).then((newAccess) => {
        originalRequest.headers.Authorization = `Bearer ${newAccess}`
        return http(originalRequest)
      })
    }

    isRefreshing = true

    try {
      const res = await axios.post(
        `${BASE_URL}/api/token/refresh/`,
        { refresh },
        { headers: { "Content-Type": "application/json" } }
      )

      const newAccess = res.data?.access
      if (!newAccess) throw new Error("No access token in refresh response")

      localStorage.setItem("access", newAccess)

      if (res.data?.refresh) {
        localStorage.setItem("refresh", res.data.refresh)
      }

      resolveQueue(null, newAccess)

      originalRequest.headers.Authorization = `Bearer ${newAccess}`
      return http(originalRequest)
    } catch (refreshErr) {
      resolveQueue(refreshErr, null)
      localStorage.removeItem("access")
      localStorage.removeItem("refresh")
      return Promise.reject(refreshErr)
    } finally {
      isRefreshing = false
    }
  }
)

export default http
