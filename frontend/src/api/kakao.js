import axios from "axios"

export function getRoute({ originX, originY, destX, destY }) {
  const origin = `${originX},${originY}`        // lng,lat
  const destination = `${destX},${destY}`       // lng,lat

  return axios.get("/api/kakao/directions/", {
    params: { origin, destination },
  })
}
