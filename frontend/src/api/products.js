import http from "@/api/http"

// 상품 목록 조회
export async function fetchProducts(type, params = {}) {
  const res = await http.get("/api/products/", { params: { type, ...params } })
  return res.data
}

// 은행 목록 조회 (DB에서 distinct)
export async function fetchBanks(type) {
  const res = await http.get("/api/products/banks/", { params: { type } })
  return res.data
}

// 상품 상세 조회
export async function fetchProductDetail(id) {
  const res = await http.get(`/api/products/${id}/`)
  return res.data
}

// 외부 API → DB 동기화
export async function syncProducts() {
  const res = await http.post("/api/products/sync/")
  return res.data
}
