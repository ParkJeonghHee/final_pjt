<template>
  <main class="container my-5">
    <div class="p-4 border rounded bg-white">
      <h4 class="fw-bold mb-3">은행지도</h4>

      <div class="row g-3">
        <!-- 좌측: 검색 UI -->
        <div class="col-md-4">
          <div class="border rounded p-3">
            <h6 class="fw-bold mb-3">은행 찾기</h6>

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
            <div v-if="selectedPlace" class="mt-3">
              <div class="fw-bold">{{ selectedPlace.place_name }}</div>
              <div class="text-muted small">
                {{ selectedPlace.road_address_name || selectedPlace.address_name }}
              </div>

              <div v-if="routeInfo" class="text-muted small mt-2">
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

// 출발지 멀티캠퍼스 역삼
const START_LAT = 37.5012743
const START_LNG = 127.039585

const mapEl = ref(null)
const region = ref("")
const district = ref("")
const bank = ref("")

const isReady = ref(false)
const message = ref("지도를 불러오는 중입니다...")
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
  clearRoute()
  const linePath = path.map((p) => new kakaoObj.maps.LatLng(p.y, p.x))
  routePolyline = new kakaoObj.maps.Polyline({
    map,
    path: linePath,
    strokeWeight: 5,
    strokeOpacity: 0.9,
    strokeStyle: "solid",
  })
}

async function requestRouteToPlace(place) {
  routeInfo.value = null
  clearRoute()

  const destLng = place.x
  const destLat = place.y

  const res = await getRoute({
    originX: START_LNG,
    originY: START_LAT,
    destX: destLng,
    destY: destLat,
  })

  const path = res?.data?.path || []
  if (path.length === 0) {
    message.value = "경로 결과가 없습니다."
    return
  }

  routeInfo.value = {
    distance: Number(res.data.distance || 0),
    duration: Number(res.data.duration || 0),
  }
  drawRoutePolyline(path)
}

async function openPlace(place) {
  selectedPlace.value = place
  routeInfo.value = null

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

  try {
    await requestRouteToPlace(place)
    message.value = "선택한 지점의 경로를 표시했습니다."
  } catch (e) {
    console.error(e)
    message.value = "경로를 불러오는 중 오류가 발생했습니다."
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
  try {
    const resp = await fetch("/data.json")
    const d = await resp.json()
    mapInfo.value = d.mapInfo || []
    bankInfo.value = d.bankInfo || []
  } catch (e) {
    console.error(e)
    message.value = "데이터 로드 실패"
  }

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

    const startPos = new kakaoObj.maps.LatLng(START_LAT, START_LNG)

    map = new kakaoObj.maps.Map(mapEl.value, {
      center: startPos,
      level: 5,
    })

    ps = new kakaoObj.maps.services.Places()
    infoWindow = new kakaoObj.maps.InfoWindow({ zIndex: 1 })

    // 출발지 마커(역삼)
    const startMarker = new kakaoObj.maps.Marker({ map, position: startPos })
    const startInfo = new kakaoObj.maps.InfoWindow({
      content: `<div style="padding:6px 8px;font-size:12px;"><b>출발지</b><br/>멀티캠퍼스(역삼)</div>`,
    })
    startInfo.open(map, startMarker)

    // 렌더 안정화
    setTimeout(() => {
      map.relayout()
      map.setCenter(startPos)
      isReady.value = true
      message.value = "찾기 버튼을 클릭하면 은행 마커가 표시됩니다."
    }, 0)
  })
})

onUnmounted(() => {
  destroyAll()
})
</script>
