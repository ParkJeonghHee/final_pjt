<template>
  <main class="container my-5">
    <div class="p-4 border rounded bg-white">
      <h4 class="fw-bold mb-3">은행지도</h4>

      <div class="row g-3">
        <!-- 좌측: 검색 UI -->
        <div class="col-md-4">
          <div class="border rounded p-3">
            <h6 class="fw-bold mb-3">은행 찾기</h6>

            <!-- 출발지 정보 -->
            <div class="alert alert-info small py-2 px-3 mb-3">
              <div class="fw-semibold">📍 출발지</div>
              <div v-if="currentLocation">
                위도: {{ currentLocation.lat.toFixed(4) }}<br/>
                경도: {{ currentLocation.lng.toFixed(4) }}
              </div>
              <div v-else class="text-muted">
                위치 요청 중...
              </div>
            </div>

            <label class="form-label mb-1">광역시/도</label>
            <select class="form-select mb-2" v-model="region">
              <option value="">선택하세요</option>
              <option v-for="r in mapInfo" :key="r.name" :value="r.name">
                {{ r.name }}
              </option>
            </select>

            <label class="form-label mb-1">시/군/구</label>
            <select class="form-select mb-2" v-model="district" :disabled="!region">
              <option value="">
                {{ region ? "선택하세요" : "광역시/도를 먼저 선택하세요" }}
              </option>
              <option v-for="d in districts" :key="d" :value="d">
                {{ d }}
              </option>
            </select>

            <label class="form-label mb-1">은행</label>
            <select class="form-select mb-3" v-model="bank" :disabled="!district">
              <option value="">
                {{ district ? "선택하세요" : "시/군/구를 먼저 선택하세요" }}
              </option>
              <option v-for="b in bankInfo" :key="b" :value="b">
                {{ b }}
              </option>
            </select>

            <button
              type="button"
              class="btn btn-success w-100"
              @click="onSearch"
              :disabled="!isReady"
            >
              찾기
            </button>

            <!-- 안내 문구 -->
            <p class="mt-3 mb-0 small text-muted">
              {{ message }}
            </p>

            <!-- 선택 지점 정보(마커 클릭 시) -->
            <div v-if="selectedPlace" class="mt-3 p-3 border rounded bg-light">
              <div class="fw-bold">{{ selectedPlace.place_name }}</div>
              <div class="text-muted small">
                {{ selectedPlace.road_address_name || selectedPlace.address_name }}
              </div>

              <!-- 경로 옵션 선택 -->
              <div class="mt-3">
                <label class="form-label fw-bold small mb-2">🚗 경로 옵션</label>
                <div class="btn-group w-100" role="group">
                  <input 
                    type="radio" 
                    class="btn-check" 
                    id="routeAuto" 
                    name="routeOption" 
                    value="auto"
                    v-model="routeOption"
                  />
                  <label class="btn btn-outline-primary btn-sm" for="routeAuto">
                    자동차
                  </label>

                  <input 
                    type="radio" 
                    class="btn-check" 
                    id="routeWalk" 
                    name="routeOption" 
                    value="walk"
                    v-model="routeOption"
                  />
                  <label class="btn btn-outline-primary btn-sm" for="routeWalk">
                    도보
                  </label>

                  <input 
                    type="radio" 
                    class="btn-check" 
                    id="routePublic" 
                    name="routeOption" 
                    value="public"
                    v-model="routeOption"
                  />
                  <label class="btn btn-outline-primary btn-sm" for="routePublic">
                    대중교통
                  </label>
                </div>
              </div>

              <button
                type="button"
                class="btn btn-primary w-100 mt-2 btn-sm"
                @click="executeRoute"
              >
                경로 실행
              </button>

              <div v-if="routeInfo && routeOption !== 'public'" class="text-muted small mt-2">
                <strong>경로 정보:</strong><br/>
                거리: {{ (routeInfo.distance / 1000).toFixed(2) }}km /
                시간: {{ Math.ceil(routeInfo.duration / 60) }}분
              </div>
            </div>

            <!-- 결과 정렬 + 결과 리스트 -->
            <div v-if="places.length" class="mt-4">
              <div class="d-flex justify-content-between align-items-center mb-2">
                <div class="fw-bold">검색 결과 ({{ places.length }})</div>

                <select
                  class="form-select form-select-sm"
                  style="width: 120px"
                  v-model="sortMode"
                >
                  <option value="distance">거리순</option>
                  <option value="name">이름순</option>
                </select>
              </div>

              <div class="list-group" style="max-height: 260px; overflow: auto">
                <button
                  v-for="p in sortedPlaces"
                  :key="placeKey(p)"
                  type="button"
                  class="list-group-item list-group-item-action"
                  @click="openPlace(p)"
                >
                  <div class="fw-semibold">{{ p.place_name }}</div>
                  <div class="small text-muted">
                    {{ p.road_address_name || p.address_name }}
                  </div>
                  <div class="small text-muted" v-if="p.distance != null">
                    현재 중심 기준 거리: {{ (Number(p.distance) / 1000).toFixed(2) }}km
                  </div>
                </button>
              </div>

              <button
                type="button"
                class="btn btn-outline-secondary btn-sm w-100 mt-2"
                @click="clearAllResults"
              >
                결과/경로 지우기
              </button>
            </div>
          </div>
        </div>

        <!-- 우측: 지도 -->
        <div class="col-md-8">
          <div ref="mapEl" style="width: 100%; height: 560px; border-radius: 8px"></div>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from "vue"
import { getRoute } from "@/api/kakao"

const mapInfo = ref([])
const bankInfo = ref([])

// GPS로 얻은 사용자 위치
const currentLocation = ref(null)

const mapEl = ref(null)
const region = ref("")
const district = ref("")
const bank = ref("")
const routeOption = ref("auto") // auto | walk | public

const isReady = ref(false)
const message = ref("위치를 요청 중입니다...")
const selectedPlace = ref(null)
const routeInfo = ref(null)

// 결과 리스트 + 정렬 모드
const places = ref([])
const sortMode = ref("distance") // distance | name

let kakaoObj = null
let map = null
let ps = null
let infoWindow = null
let markers = []
let routePolyline = null
let startMarker = null
let startInfo = null

// placeKey -> marker 매핑(리스트 클릭 시 marker 찾기)
const markerMap = new Map()

const districts = computed(() => {
  const r = mapInfo.value.find((x) => x.name === region.value)
  return r ? r.countries : []
})

watch(region, () => {
  district.value = ""
  bank.value = ""
})
watch(district, () => {
  bank.value = ""
})

function placeKey(place) {
  return place.id || `${place.x}:${place.y}:${place.place_name}`
}

const sortedPlaces = computed(() => {
  const list = [...places.value]

  if (sortMode.value === "name") {
    return list.sort((a, b) => (a.place_name || "").localeCompare(b.place_name || ""))
  }

  // distance 기본 (places API distance는 문자열일 수 있음)
  return list.sort((a, b) => {
    const da = a.distance != null ? Number(a.distance) : Number.POSITIVE_INFINITY
    const db = b.distance != null ? Number(b.distance) : Number.POSITIVE_INFINITY
    return da - db
  })
})

function clearMarkers() {
  markers.forEach((m) => m.setMap(null))
  markers = []
  markerMap.clear()
}

function clearRoute() {
  if (routePolyline) {
    routePolyline.setMap(null)
    routePolyline = null
  }
}

// “조용히” 결과만 정리 (message는 건드리지 않음)
function resetResultsSilently() {
  selectedPlace.value = null
  routeInfo.value = null
  places.value = []
  clearRoute()
  clearMarkers()
  if (infoWindow) infoWindow.close()
}

function clearAllResults() {
  resetResultsSilently()
  message.value = "결과를 정리했습니다."
}

function destroyAll() {
  try {
    clearRoute()
    clearMarkers()
    if (infoWindow) infoWindow.close()
  } catch (_) {}
  infoWindow = null
  ps = null
  map = null
  kakaoObj = null
}

function drawRoutePolyline(path) {
  console.log("\n=== [drawRoutePolyline] ✅ 함수 호출됨 ===")
  // 기존 폴리라인 제거
  clearRoute()

  // ✅ 입력값 검증
  console.log("[drawRoutePolyline] 입력값 검증 시작", {
    pathExists: !!path,
    pathLength: path?.length,
    isArray: Array.isArray(path),
  })

  if (!path || path.length === 0) {
    console.error("[drawRoutePolyline] ❌ 경로 데이터가 없습니다.")
    return
  }

  console.log("[drawRoutePolyline] ✅ 경로 데이터 존재")

  // ✅ 카카오 객체 검증
  if (!kakaoObj || !kakaoObj.maps) {
    console.error("[drawRoutePolyline] ❌ kakaoObj 미초기화", { kakaoObj })
    return
  }

  console.log("[drawRoutePolyline] ✅ kakaoObj 초기화됨")

  // ✅ 지도 객체 검증
  if (!map) {
    console.error("[drawRoutePolyline] ❌ map 미초기화")
    return
  }

  console.log("[drawRoutePolyline] ✅ map 초기화됨")

  try {
    console.log("[drawRoutePolyline] 좌표 변환 시작 (LatLng)...")
    
    // ✅ 좌표를 LatLng 객체로 변환
    const linePath = path
      .map((p, idx) => {
        if (!p || typeof p.x === "undefined" || typeof p.y === "undefined") {
          console.warn(`[drawRoutePolyline] ⚠️ 유효하지 않은 좌표[${idx}]:`, p)
          return null
        }
        return new kakaoObj.maps.LatLng(p.y, p.x)
      })
      .filter((p) => p !== null)

    console.log(`[drawRoutePolyline] 좌표 변환 완료: ${path.length} → ${linePath.length}개`)

    // ✅ 최소 2개 이상의 좌표 필요
    if (linePath.length < 2) {
      console.error("[drawRoutePolyline] ❌ 유효한 좌표 부족:", linePath.length)
      return
    }

    console.log("[drawRoutePolyline] ✅ 유효한 좌표 충분함:", linePath.length)

    // ✅ 폴리라인 생성
    console.log("[drawRoutePolyline] Polyline 객체 생성 중...")
    
    routePolyline = new kakaoObj.maps.Polyline({
      map,
      path: linePath,
      strokeWeight: 5,
      strokeOpacity: 0.9,
      strokeStyle: "solid",
      strokeColor: "#FF0000", // 빨간색으로 명확하게 표시
    })

    console.log("[drawRoutePolyline] ✅ Polyline 객체 생성 완료")

    // ✅ 폴리라인이 정상적으로 생성됐는지 확인
    if (!routePolyline) {
      console.error("[drawRoutePolyline] ❌ Polyline 객체가 null")
      return
    }

    console.log("[drawRoutePolyline] ✅ Polyline 객체 존재 확인 완료")

    // ✅ Polyline 상태 확인
    const mapAssigned = routePolyline.getMap()
    const pathArray = routePolyline.getPath()
    const pathLength = pathArray?.length || 0
    const color = routePolyline.getStrokeColor?.()
    const weight = routePolyline.getStrokeWeight?.()

    console.log("[drawRoutePolyline] ✅ Polyline 상태 확인:", {
      mapAssigned: mapAssigned !== null && mapAssigned !== undefined,
      pathLength,
      color,
      weight,
      zIndex: routePolyline.zIndex,
    })

    if (!mapAssigned) {
      console.error("[drawRoutePolyline] ⚠️ 경고: Polyline이 map에 할당되지 않음")
    }

    console.log("\n=== [drawRoutePolyline] ✅ 완료 ===")

  } catch (err) {
    console.error("[drawRoutePolyline] ❌ 예외 발생:", {
      message: err.message,
      name: err.name,
      stack: err.stack,
    })
  }
}

async function requestRouteToPlace(place, priority = "RECOMMEND") {
  console.log("\n=== [requestRouteToPlace] ✅ 함수 호출됨 ===")
  
  routeInfo.value = null
  clearRoute()

  if (!currentLocation.value) {
    message.value = "출발지 위치를 얻을 수 없습니다."
    console.error("[requestRouteToPlace] ❌ currentLocation 없음")
    return
  }

  console.log("[requestRouteToPlace] ✅ currentLocation 확인됨:", currentLocation.value)

  const destLng = place.x
  const destLat = place.y

  try {
    console.log("[requestRouteToPlace] 📍 목적지:", {
      place: place.place_name,
      x: destLng,
      y: destLat,
    })

    console.log("[requestRouteToPlace] 🚀 API 요청 파라미터:", {
      originX: currentLocation.value.lng,
      originY: currentLocation.value.lat,
      destX: destLng,
      destY: destLat,
      priority,
    })

    console.log("[requestRouteToPlace] 네트워크 요청 시작...")
    const res = await getRoute({
      originX: currentLocation.value.lng,
      originY: currentLocation.value.lat,
      destX: destLng,
      destY: destLat,
      priority: priority,
    })

    console.log("[requestRouteToPlace] ✅ API 응답 수신", {
      status: res.status,
      statusText: res.statusText,
      hasData: !!res.data,
    })

    console.log("[requestRouteToPlace] 응답 상세:", {
      distance: res.data?.distance,
      duration: res.data?.duration,
      pathLength: res.data?.path?.length,
      priority: res.data?.priority,
    })

    const path = res?.data?.path || []

    console.log("[requestRouteToPlace] 📊 경로 배열 상태:", {
      exists: path !== undefined,
      isNull: path === null,
      isArray: Array.isArray(path),
      length: path?.length,
      isEmpty: path?.length === 0,
      sampleFirst: path?.[0],
      sampleLast: path?.[path.length - 1],
    })

    if (!path || path.length === 0) {
      message.value = "경로 결과가 없습니다. (빈 경로 배열)"
      console.error("[requestRouteToPlace] ❌ 빈 경로 배열:", { path })
      return
    }

    console.log(`[requestRouteToPlace] ✅ 경로 좌표 개수: ${path.length}개`)

    routeInfo.value = {
      distance: Number(res.data.distance || 0),
      duration: Number(res.data.duration || 0),
    }

    console.log("[requestRouteToPlace] ✅ routeInfo 설정:", routeInfo.value)
    console.log("[requestRouteToPlace] drawRoutePolyline 함수 호출...")

    drawRoutePolyline(path)
    
    console.log("[requestRouteToPlace] ✅ 완료")
  } catch (e) {
    console.error("[requestRouteToPlace] ❌ 예외 발생:", {
      name: e.name,
      message: e.message,
      code: e.code,
    })
    console.error("[requestRouteToPlace] 응답 에러:", {
      status: e.response?.status,
      statusText: e.response?.statusText,
      data: e.response?.data,
    })
    console.error("[requestRouteToPlace] 스택트레이스:", e.stack)
    
    message.value = `경로 조회 실패: ${e.response?.data?.detail || e.message}`
  }
}

async function openPlace(place) {
  selectedPlace.value = place
  routeInfo.value = null
  routeOption.value = "auto"

  const key = placeKey(place)
  const marker = markerMap.get(key)

  const pos = new kakaoObj.maps.LatLng(place.y, place.x)
  map.panTo(pos)

  if (marker && infoWindow) {
    infoWindow.setContent(
      `<div style="padding:6px 8px;font-size:12px;">
        <b>${place.place_name}</b><br/>
        ${place.road_address_name || place.address_name}
      </div>`
    )
    infoWindow.open(map, marker)
  }
}

function displayPlaces(list) {
  places.value = list
  markerMap.clear()

  const bounds = new kakaoObj.maps.LatLngBounds()

  list.forEach((place) => {
    const pos = new kakaoObj.maps.LatLng(place.y, place.x)
    const marker = new kakaoObj.maps.Marker({ map, position: pos })
    markers.push(marker)
    bounds.extend(pos)

    markerMap.set(placeKey(place), marker)

    kakaoObj.maps.event.addListener(marker, "click", async () => {
      await openPlace(place)
    })
  })

  map.setBounds(bounds)
}

function placesSearchCB(data, status) {
  if (!kakaoObj?.maps?.services) {
    message.value = "Places 서비스를 사용할 수 없습니다. (libraries=services 확인)"
    return
  }

  if (status === kakaoObj.maps.services.Status.OK) {
    message.value = "마커가 표시되었습니다. 왼쪽 리스트/마커 클릭 시 경로가 출력됩니다."
    displayPlaces(data)
  } else if (status === kakaoObj.maps.services.Status.ZERO_RESULT) {
    resetResultsSilently()
    message.value = "검색 결과가 없습니다."
  } else {
    resetResultsSilently()
    message.value = "은행 지점 검색 중 오류가 발생했습니다."
  }
}

async function executeRoute() {
  console.log("\n=== [executeRoute] ✅ 함수 호출됨 ===")
  
  if (!selectedPlace.value || !currentLocation.value) {
    message.value = "선택된 지점이 없거나 위치를 알 수 없습니다."
    console.error("[executeRoute] ❌ 입력값 검증 실패:", {
      selectedPlace: selectedPlace.value,
      currentLocation: currentLocation.value,
      hasPlace: !!selectedPlace.value,
      hasLocation: !!currentLocation.value,
    })
    return
  }

  console.log("[executeRoute] ✅ 입력값 검증 완료", {
    place: selectedPlace.value.place_name,
    location: currentLocation.value,
  })

  console.log("[executeRoute] 📋 routeOption 확인:", routeOption.value)

  if (routeOption.value === "public") {
    console.log("[executeRoute] 🚌 대중교통 선택됨 (카카오맵 링크 열기)")
    // 대중교통: 카카오맵 길찾기 링크 열기
    const kakaoMapUrl = `https://map.kakao.com/link/to/${encodeURIComponent(
      selectedPlace.value.place_name
    )},${selectedPlace.value.y},${selectedPlace.value.x}`
    console.log("[executeRoute] 카카오맵 URL:", kakaoMapUrl)
    window.open(kakaoMapUrl, "_blank")
    message.value = "카카오맵 길찾기를 새 탭에서 열었습니다."
  } else {
    console.log("[executeRoute] 🚗 백엔드 경로 요청 모드:", routeOption.value)
    // 자동차/도보: 백엔드 API 호출
    // 자동차/도보: 백엔드 API 호출
    const priorityMap = {
      auto: "RECOMMEND", // 자동차 추천 경로
      walk: "MIN_TIME", // 도보는 시간 최소화
    }
    const priority = priorityMap[routeOption.value] || "RECOMMEND"

    console.log("[executeRoute] 파라미터 매핑:", { routeOption: routeOption.value, priority })

    await requestRouteToPlace(selectedPlace.value, priority)
    message.value = `${routeOption.value === "auto" ? "자동차" : "도보"} 경로를 표시했습니다.`
  }
}

function onSearch() {
  if (!isReady.value || !map || !ps) {
    message.value = "지도가 아직 준비되지 않았습니다."
    return
  }

  if (!region.value || !district.value || !bank.value) {
    resetResultsSilently()
    message.value = "광역시/도, 시/군/구, 은행을 모두 선택해주세요."
    return
  }

  // 검색 전 초기화
  resetResultsSilently()

  const keyword = `${region.value} ${district.value} ${bank.value}`
  const center = map.getCenter()

  ps.keywordSearch(keyword, placesSearchCB, {
    location: center,
    radius: 5000,
    sort: kakaoObj.maps.services.SortBy.DISTANCE,
  })
}

onMounted(async () => {
  // 1. GPS 위치 요청
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        currentLocation.value = {
          lat: position.coords.latitude,
          lng: position.coords.longitude,
        }
        message.value = "위치를 확인했습니다. 데이터를 로드 중입니다..."
      },
      (error) => {
        console.warn("GPS 위치 요청 실패:", error)
        message.value = "GPS 위치를 얻을 수 없습니다. (권한 확인 필요)"
        // GPS 실패 시에도 계속 진행
      }
    )
  } else {
    message.value = "이 브라우저는 Geolocation을 지원하지 않습니다."
  }

  // 2. 데이터 로드
  try {
    const resp = await fetch("/data.json")
    const d = await resp.json()
    mapInfo.value = d.mapInfo || []
    bankInfo.value = d.bankInfo || []
  } catch (e) {
    console.error(e)
    message.value = "데이터 로드 실패"
  }

  // 3. 카카오 지도 SDK 확인
  if (!window.kakao || !window.kakao.maps) {
    message.value = "카카오 지도 SDK 로드 실패 (index.html 로드/키/플랫폼 등록 확인)"
    isReady.value = false
    return
  }

  kakaoObj = window.kakao

  kakaoObj.maps.load(() => {
    if (!mapEl.value) {
      message.value = "지도 컨테이너가 없습니다."
      return
    }

    if (!kakaoObj.maps.services) {
      message.value = "services 라이브러리가 없습니다. (libraries=services 확인)"
      return
    }

    // 사용자 GPS 위치 또는 기본값(서울시청) 사용
    const initialLat = currentLocation.value?.lat || 37.5665
    const initialLng = currentLocation.value?.lng || 126.978
    const initialPos = new kakaoObj.maps.LatLng(initialLat, initialLng)

    map = new kakaoObj.maps.Map(mapEl.value, {
      center: initialPos,
      level: 5,
    })

    ps = new kakaoObj.maps.services.Places()
    infoWindow = new kakaoObj.maps.InfoWindow({ zIndex: 1 })

    // 출발지 마커 표시
    startMarker = new kakaoObj.maps.Marker({ map, position: initialPos })
    const markerLabel = currentLocation.value
      ? "📍 현재 위치"
      : "📍 기본 위치(서울시청)"
    startInfo = new kakaoObj.maps.InfoWindow({
      content: `<div style="padding:6px 8px;font-size:12px;"><b>${markerLabel}</b><br/>위도: ${initialLat.toFixed(4)}<br/>경도: ${initialLng.toFixed(4)}</div>`,
    })
    startInfo.open(map, startMarker)

    // 렌더 안정화
    setTimeout(() => {
      map.relayout()
      map.setCenter(initialPos)
      isReady.value = true
      message.value = currentLocation.value
        ? "위치가 확인되었습니다. 은행을 검색해주세요."
        : "GPS 위치 없음. 기본 위치(서울시청)에서 시작합니다. 은행을 검색해주세요."
    }, 0)
  })
})

onUnmounted(() => {
  destroyAll()
})
</script>
