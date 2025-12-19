import http from "@/api/http"

export async function fetchProductList(type, params = {}) {
  const res = await http.get("/api/products/", { params: { type, ...params } })
  return res.data
}

export async function fetchBanks(type) {
  const res = await http.get("/api/products/banks/", { params: { type } })
  return res.data
}

export async function fetchProductDetail(id) {
  const res = await http.get(`/api/products/${id}/`)
  return res.data
}
