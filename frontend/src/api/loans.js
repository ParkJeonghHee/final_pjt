import http from "@/api/http"

export async function fetchLoans(params = {}) {
  const res = await http.get("/api/loans/", { params })
  return res.data
}
