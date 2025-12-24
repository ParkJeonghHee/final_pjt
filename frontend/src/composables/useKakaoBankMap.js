import { ref } from "vue"
import { getRoute } from "@/api/kakao"

export function useKakaoBankMap() {
  const currentLocation = ref(null)

  let kakaoObj = null
  let map = null
  let ps = null
  let geocoder = null
  let markers = []
  let routePolyline = null

  let startMarker = null
  let startInfo = null

  function clearMarkers() {
    markers.forEach((m) => m.setMap(null))
    markers = []
  }

  function clearRoute() {
    if (routePolyline) {
      routePolyline.setMap(null)
      routePolyline = null
    }
  }

  function setCurrentLocationMarker(lat, lng) {
    if (!map || !kakaoObj) return
    const pos = new kakaoObj.maps.LatLng(lat, lng)

    if (!startMarker) {
      startMarker = new kakaoObj.maps.Marker({ map, position: pos })
    } else {
      startMarker.setPosition(pos)
      startMarker.setMap(map)
    }

    const content = `
      <div style="padding:6px 8px;font-size:12px;">
        <b>📍 현재 위치</b><br/>
        위도: ${Number(lat).toFixed(4)}<br/>
        경도: ${Number(lng).toFixed(4)}
      </div>
    `

    if (!startInfo) {
      startInfo = new kakaoObj.maps.InfoWindow({ content, zIndex: 2 })
      startInfo.open(map, startMarker)
    } else {
      startInfo.setContent(content)
      startInfo.open(map, startMarker)
    }
  }

  async function initMap(mapEl) {
    if (!window.kakao || !window.kakao.maps) throw new Error("카카오 지도 SDK 로드 실패")
    kakaoObj = window.kakao

    return new Promise((resolve) => {
      kakaoObj.maps.load(() => {
        const initialLat = currentLocation.value?.lat || 37.5665
        const initialLng = currentLocation.value?.lng || 126.978
        const initialPos = new kakaoObj.maps.LatLng(initialLat, initialLng)

        map = new kakaoObj.maps.Map(mapEl, { center: initialPos, level: 5 })
        ps = new kakaoObj.maps.services.Places()
        geocoder = new kakaoObj.maps.services.Geocoder()

        if (currentLocation.value) {
          setCurrentLocationMarker(currentLat(), currentLng())
          map.setCenter(initialPos)
        } else {
          setCurrentLocationMarker(initialLat, initialLng)
        }

        requestAnimationFrame(() => map && map.relayout())
        resolve()
      })
    })
  }

  function currentLat() {
    return currentLocation.value?.lat
  }
  function currentLng() {
    return currentLocation.value?.lng
  }

  function panTo(x, y) {
    if (!map || !kakaoObj) return
    map.panTo(new kakaoObj.maps.LatLng(y, x))
  }

  function fitPlaces(places, onMarkerClick) {
    if (!map || !kakaoObj || !places?.length) return

    clearMarkers()

    const bounds = new kakaoObj.maps.LatLngBounds()
    places.forEach((p) => {
      const pos = new kakaoObj.maps.LatLng(p.y, p.x)
      const marker = new kakaoObj.maps.Marker({ map, position: pos })
      markers.push(marker)
      bounds.extend(pos)
      if (onMarkerClick) marker.addListener("click", () => onMarkerClick(p))
    })

    map.setBounds(bounds)
    requestAnimationFrame(() => map && map.relayout())
  }

  function drawRoutePolyline(path) {
    clearRoute()
    if (!Array.isArray(path) || !path.length || !kakaoObj || !map) return

    const toLatLng = (p) => {
      if (!p) return null
      let x = p.x ?? p.lng ?? p.lon ?? p.longitude
      let y = p.y ?? p.lat ?? p.latitude
      if (Array.isArray(p) && p.length >= 2) { x = p[0]; y = p[1] }
      x = Number(x); y = Number(y)
      if (!Number.isFinite(x) || !Number.isFinite(y)) return null
      return new kakaoObj.maps.LatLng(y, x)
    }

    const linePath = path.map(toLatLng).filter(Boolean)
    if (linePath.length < 2) return

    routePolyline = new kakaoObj.maps.Polyline({
      map,
      path: linePath,
      strokeWeight: 5,
      strokeOpacity: 0.9,
      strokeStyle: "solid",
      strokeColor: "#FF0000",
    })

    const bounds = new kakaoObj.maps.LatLngBounds()
    linePath.forEach((latlng) => bounds.extend(latlng))
    map.setBounds(bounds, 60, 60, 60, 420)
    requestAnimationFrame(() => map && map.relayout())
  }

  function keywordSearch(query, options) {
    return new Promise((resolve) => {
      ps.keywordSearch(query, (data, status) => resolve({ data, status }), options)
    })
  }

  function geocodeAddress(address) {
    return new Promise((resolve) => {
      if (!geocoder || !address) return resolve(null)
      geocoder.addressSearch(address, (result, status) => {
        if (status === kakaoObj.maps.services.Status.OK && result?.length) {
          const x = parseFloat(result[0].x)
          const y = parseFloat(result[0].y)
          if (!Number.isNaN(x) && !Number.isNaN(y)) return resolve({ x, y })
        }
        resolve(null)
      })
    })
  }

  async function requestRouteTo(place) {
    if (!place || !currentLocation.value) throw new Error("위치/목적지 없음")

    const res = await getRoute({
      originX: currentLocation.value.lng,
      originY: currentLocation.value.lat,
      destX: place.x,
      destY: place.y,
      priority: "RECOMMEND",
    })

    const path = res?.data?.path || []
    if (!path.length) throw new Error("경로 없음")

    drawRoutePolyline(path)

    return {
      distanceText: `${(res.data.distance / 1000).toFixed(2)}km`,
      durationText: `${Math.ceil(res.data.duration / 60)}분`,
    }
  }

  return {
    currentLocation,
    initMap,
    setCurrentLocationMarker,
    panTo,
    fitPlaces,
    clearMarkers,
    clearRoute,
    requestRouteTo,
    keywordSearch,
    geocodeAddress,
  }
}
