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
          </div>
        </div>

        <!-- 우측: 지도 -->
        <div class="col-md-8">
          <div ref="mapEl" style="width: 100%; height: 560px; border-radius: 8px;"></div>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from "vue"
import { getRoute } from "@/api/kakao"
import data from "@/assets/data.json"

const mapInfo = data.mapInfo
const bankInfo = data.bankInfo

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

let kakaoObj = null
let map = null
let ps = null
let infoWindow = null
let markers = []
let routePolyline = null

const districts = computed(() => {
  const r = mapInfo.find((x) => x.name === region.value)
  return r ? r.countries : []
})

watch(region, () => {
  district.value = ""
  bank.value = ""
})
watch(district, () => {
  bank.value = ""
})

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

function destroyAll() {
  clearRoute()
  clearMarkers()
  if (infoWindow) {
    try { infoWindow.close() } catch (_) {}
  }
  infoWindow = null
  ps = null
  map = null
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

  const path = res.data.path || []
  if (path.length === 0) {
    message.value = "경로 결과가 없습니다."
    return
  }

  routeInfo.value = { distance: res.data.distance, duration: res.data.duration }
  drawRoutePolyline(path)
}

function displayPlaces(places) {
  const bounds = new kakaoObj.maps.LatLngBounds()

  places.forEach((place) => {
    const pos = new kakaoObj.maps.LatLng(place.y, place.x)
    const marker = new kakaoObj.maps.Marker({ map, position: pos })
    markers.push(marker)
    bounds.extend(pos)

    kakaoObj.maps.event.addListener(marker, "click", async () => {
      selectedPlace.value = place
      routeInfo.value = null

      infoWindow.setContent(
        `<div style="padding:6px 8px;font-size:12px;">
          <b>${place.place_name}</b><br/>
          ${place.road_address_name || place.address_name}
        </div>`
      )
      infoWindow.open(map, marker)

      try {
        await requestRouteToPlace(place)
        message.value = "마커 클릭 시 경로 및 인포윈도우 출력"
      } catch (e) {
        console.error(e)
        message.value = "경로를 불러오는 중 오류가 발생했습니다."
      }
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
    message.value = "마커가 표시되었습니다. 마커를 클릭하면 경로가 출력됩니다."
    displayPlaces(data)
  } else if (status === kakaoObj.maps.services.Status.ZERO_RESULT) {
    message.value = "검색 결과가 없습니다."
    clearMarkers()
  } else {
    message.value = "은행 지점 검색 중 오류가 발생했습니다."
    clearMarkers()
  }
}

function onSearch() {
  if (!isReady.value || !map || !ps) {
    message.value = "지도가 아직 준비되지 않았습니다."
    return
  }

  selectedPlace.value = null
  routeInfo.value = null
  clearRoute()

  if (!region.value || !district.value || !bank.value) {
    message.value = "광역시/도, 시/군/구, 은행을 모두 선택해주세요."
    clearMarkers()
    if (infoWindow) infoWindow.close()
    return
  }

  const keyword = `${region.value} ${district.value} ${bank.value}`

  clearMarkers()
  if (infoWindow) infoWindow.close()

  const center = map.getCenter()

  ps.keywordSearch(keyword, placesSearchCB, {
    location: center,
    radius: 5000,
    sort: kakaoObj.maps.services.SortBy.DISTANCE,
  })
}

onMounted(() => {
  // index.html에서 sdk.js가 로드되어 있어야 함
  if (!window.kakao || !window.kakao.maps) {
    message.value = "카카오 지도 SDK 로드 실패 (index.html 로드/키/플랫폼 등록 확인)"
    isReady.value = false
    return
  }

  kakaoObj = window.kakao

  // autoload=false 이므로 반드시 load로 감싸야 함
  kakaoObj.maps.load(() => {
    if (!mapEl.value) {
      message.value = "지도 컨테이너가 없습니다."
      return
    }

    if (!kakaoObj.maps.services) {
      message.value = "services 라이브러리가 없습니다. (libraries=services 확인)"
      return
    }

    map = new kakaoObj.maps.Map(mapEl.value, {
      center: new kakaoObj.maps.LatLng(START_LAT, START_LNG),
      level: 5,
    })

    ps = new kakaoObj.maps.services.Places()
    infoWindow = new kakaoObj.maps.InfoWindow({ zIndex: 1 })

    // 출발지 마커(역삼)
    const startPos = new kakaoObj.maps.LatLng(START_LAT, START_LNG)
    const startMarker = new kakaoObj.maps.Marker({ map, position: startPos })
    const startInfo = new kakaoObj.maps.InfoWindow({
      content: `<div style="padding:6px 8px;font-size:12px;"><b>출발지</b><br/>멀티캠퍼스(역삼)</div>`,
    })
    startInfo.open(map, startMarker)

    // 처음 로딩 시 지도 강제 갱신
    setTimeout(() => {
      map.relayout()
      map.setCenter(startPos)
      isReady.value = true
      message.value = "찾기 버튼을 클릭하면 은행 마커가 표시됩니다. 마커 클릭 시 경로가 출력됩니다."
    }, 0)
  })
})

onUnmounted(() => {
  destroyAll()
})
</script>
