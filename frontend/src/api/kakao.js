import http from "@/api/http"

export function getRoute({ originX, originY, destX, destY }) {
  return http.get("/api/kakao/route/", {
    params: {
      origin: `${originX},${originY}`,
      destination: `${destX},${destY}`,
    },
  })
}
