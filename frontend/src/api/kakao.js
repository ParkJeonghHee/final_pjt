import axios from "axios"

// 자동차 
export function getRoute({ originX, originY, destX, destY, priority = "RECOMMEND" }) {
  const origin = `${originX},${originY}`         // lng,lat
  const destination = `${destX},${destY}`        // lng,lat

  return axios.get("/api/kakao/directions/", {
    params: {
      origin,
      destination,
      priority,  // 경로 옵션: RECOMMEND(추천), HIGH_SPEED(빠른 경로), MIN_TIME(시간 최단), MIN_DISTANCE(거리 최단)
    },
  })
}
