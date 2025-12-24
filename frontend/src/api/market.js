import http from "@/api/http"

export async function fetchMarketSummary() {
  const res = await http.get("/api/market/summary/")
  return res.data
}

export async function fetchMarketHistory(years = 3) {
  const res = await http.get("/api/market/history/", { params: { years } })
  return res.data
}
