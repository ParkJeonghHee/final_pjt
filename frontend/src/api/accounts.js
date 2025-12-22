import http from "@/api/http"

export const fetchProfile = () =>
  http.get("/api/accounts/profile/")

export const updateProfile = (payload) =>
  http.patch("/api/accounts/profile/", payload)
