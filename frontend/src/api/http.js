import axios from "axios"

const http = axios.create({
  baseURL: "http://127.0.0.1:8000",
  headers: {
    "Content-Type": "application/json",
  },
})

http.interceptors.request.use(
  (config) => {
    const access = localStorage.getItem("access")
    if (access) {
      config.headers.Authorization = `Bearer ${access}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

export default http
