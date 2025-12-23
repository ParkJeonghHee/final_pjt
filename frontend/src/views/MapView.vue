<template>
  <div class="page">
    <div class="page-head">
      <h2 class="page-title">은행지도</h2>
      <p class="page-sub">가까운 은행을 찾아보세요</p>
    </div>

    <div class="grid">
      <aside class="card side-card">
        <h5 class="card-title">은행 찾기</h5>

        <div class="mb-3">
          <div class="input-group input-group-sm">
            <span class="input-group-text">
              <i class="bi bi-search"></i>
            </span>
            <input
              v-model="keyword"
              class="form-control"
              placeholder="은행명 또는 주소 검색"
              @keyup.enter="onSearch"
            />
          </div>
        </div>

        <div class="divider"></div>

        <div class="mb-2">
          <label class="form-label small text-muted">광역시/도</label>
          <select v-model="selectedSido" class="form-select form-select-sm" @change="onChangeSido">
            <option value="">선택</option>
            <option v-for="s in sidos" :key="s" :value="s">{{ s }}</option>
          </select>
        </div>

        <div class="mb-2">
          <label class="form-label small text-muted">시/군/구</label>
          <select v-model="selectedSigungu" class="form-select form-select-sm" :disabled="!selectedSido">
            <option value="">선택</option>
            <option v-for="g in sigungus" :key="g" :value="g">{{ g }}</option>
          </select>
        </div>

        <div class="mb-3">
          <label class="form-label small text-muted">은행</label>
          <select v-model="selectedBank" class="form-select form-select-sm">
            <option value="">선택</option>
            <option v-for="b in banks" :key="b" :value="b">{{ b }}</option>
          </select>
        </div>

        <button class="btn btn-success w-100 btn-sm" @click="onSearch">
          <i class="bi bi-search me-1"></i> 찾기
        </button>

        <div class="hint">
          거리가 가까운 곳 먼저 조회됩니다.
        </div>

        <div class="result-head">
          <div class="small fw-semibold">검색 결과 ({{ results.length }})</div>
          <select v-model="sortMode" class="form-select form-select-sm sort">
            <option value="distance">거리순</option>
            <option value="name">이름순</option>
          </select>
        </div>

        <div class="result-list">
          <div v-if="!results.length" class="empty-note text-muted small">
            검색 결과가 없습니다.
          </div>

          <button
            v-for="place in sortedResults"
            :key="place.id"
            type="button"
            class="result-item"
            :class="{ active: selectedPlace?.id === place.id }"
            @click="selectPlace(place)"
          >
            <div class="d-flex align-items-start gap-2">
              <div class="avatar">
                <i class="bi bi-bank"></i>
              </div>

              <div class="flex-grow-1">
                <div class="d-flex justify-content-between align-items-start">
                  <div>
                    <div class="name">{{ place.name }}</div>
                    <div class="addr">{{ place.address }}</div>
                  </div>

                  <div class="text-end">
                    <div class="dist">{{ formatKm(place.distanceKm) }}</div>
                    <div class="more">자세히 보기 →</div>
                  </div>
                </div>
              </div>
            </div>
          </button>

          <button
            v-if="results.length"
            class="btn btn-outline-secondary w-100 btn-sm mt-2"
            @click="clearResults"
          >
            결과/검색 지우기
          </button>
        </div>
      </aside>

      <section class="card map-card">
        <div class="map-card-head">은행지도</div>

        <div class="map-card-body">
          <div class="map-area">
            <div class="map-canvas" ref="mapEl"></div>

            <div class="route-panel card shadow-sm" v-if="selectedPlace">
              <div class="card-body p-3">
                <div class="d-flex justify-content-between align-items-start">
                  <div>
                    <div class="fw-bold">{{ selectedPlace.name }}</div>
                    <div class="small text-muted">{{ selectedPlace.address }}</div>
                  </div>
                  <button class="btn btn-sm btn-light" @click="selectedPlace = null" aria-label="닫기">
                    <i class="bi bi-x"></i>
                  </button>
                </div>

                <div class="btn-group w-100 mt-3" role="group" aria-label="경로 옵션">
                  <button
                    class="btn btn-sm"
                    :class="routeMode==='car' ? 'btn-primary' : 'btn-outline-primary'"
                    @click="routeMode='car'; requestRoute()"
                  >
                    자동차
                  </button>
                  <button
                    class="btn btn-sm"
                    :class="routeMode==='walk' ? 'btn-primary' : 'btn-outline-primary'"
                    @click="routeMode='walk'; requestRoute()"
                  >
                    도보
                  </button>
                  <button
                    class="btn btn-sm"
                    :class="routeMode==='transit' ? 'btn-primary' : 'btn-outline-primary'"
                    @click="routeMode='transit'; requestRoute()"
                  >
                    대중교통
                  </button>
                </div>

                <div class="mt-3 small">
                  <div class="d-flex justify-content-between">
                    <span class="text-muted">거리</span>
                    <span class="fw-semibold">{{ routeInfo?.distanceText || '-' }}</span>
                  </div>
                  <div class="d-flex justify-content-between mt-1">
                    <span class="text-muted">시간</span>
                    <span class="fw-semibold">{{ routeInfo?.durationText || '-' }}</span>
                  </div>
                </div>

                <button class="btn btn-success btn-sm w-100 mt-3" @click="requestRoute">
                  경로 검색
                </button>
              </div>
            </div>
          </div><!-- /map-area -->
        </div><!-- /map-card-body -->
      </section>
    </div><!-- /grid -->
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from "vue"
import { getRoute } from "@/api/kakao"

const keyword = ref("")
const selectedSido = ref("")
const selectedSigungu = ref("")
const selectedBank = ref("")
const selectedPlace = ref(null)
const routeMode = ref("car")
const sortMode = ref("distance")
const results = ref([])
const routeInfo = ref(null)
const currentLocation = ref(null)
const mapEl = ref(null)

let kakaoObj = null
let map = null
let ps = null
let infoWindow = null
let markers = []
let routePolyline = null
let startMarker = null
let startInfo = null

const mapInfo = ref([])
const bankInfo = ref([])

const sidos = computed(() => mapInfo.value.map((x) => x.name) || [])
const sigungus = computed(() => {
  const found = mapInfo.value.find((x) => x.name === selectedSido.value)
  return found ? found.countries : []
})
const banks = computed(() => bankInfo.value || [])

const sortedResults = computed(() => {
  const list = [...results.value]
  if (sortMode.value === "name") return list.sort((a, b) => (a.name || "").localeCompare(b.name || ""))
  return list.sort((a, b) => (a.distanceKm ?? Infinity) - (b.distanceKm ?? Infinity))
})

watch(selectedSido, () => {
  selectedSigungu.value = ""
  selectedBank.value = ""
})

function formatKm(km) {
  if (!km) return "-"
  return km < 1 ? `${Math.round(km * 1000)}m` : `${km.toFixed(1)}km`
}

function onChangeSido() {
  selectedSigungu.value = ""
  selectedBank.value = ""
}

function selectPlace(place) {
  selectedPlace.value = place
  routeMode.value = "car"
  routeInfo.value = null

  if (map && place.x && place.y) {
    const pos = new kakaoObj.maps.LatLng(place.y, place.x)
    map.panTo(pos)
  }
}

function clearResults() {
  results.value = []
  selectedPlace.value = null
  routeInfo.value = null
  clearRoute()
}

function clearRoute() {
  if (routePolyline) {
    routePolyline.setMap(null)
    routePolyline = null
  }
}

function clearMarkers() {
  markers.forEach((m) => m.setMap(null))
  markers = []
}

function destroyAll() {
  try {
    clearRoute()
    clearMarkers()
    if (infoWindow) infoWindow.close()
    if (startInfo) startInfo.close()
  } catch (_) {}
  startInfo = null
  infoWindow = null
  ps = null
  map = null
  kakaoObj = null
}

function drawRoutePolyline(path) {
  clearRoute()
  if (!path?.length || !kakaoObj || !map) return

  const linePath = path
    .map((p) => (p && p.x != null && p.y != null ? new kakaoObj.maps.LatLng(p.y, p.x) : null))
    .filter(Boolean)

  if (linePath.length < 2) return

  routePolyline = new kakaoObj.maps.Polyline({
    map,
    path: linePath,
    strokeWeight: 5,
    strokeOpacity: 0.9,
    strokeStyle: "solid",
    strokeColor: "#FF0000",
  })
}

async function requestRoute() {
  if (!selectedPlace.value || !currentLocation.value) {
    alert("선택된 지점이 없거나 위치를 알 수 없습니다")
    return
  }

  if (routeMode.value === "transit") {
    const kakaoMapUrl = `https://map.kakao.com/link/to/${encodeURIComponent(selectedPlace.value.name)},${selectedPlace.value.y},${selectedPlace.value.x}`
    window.open(kakaoMapUrl, "_blank")
    return
  }

  routeInfo.value = null
  clearRoute()

  const priority = routeMode.value === "walk" ? "MIN_TIME" : "RECOMMEND"

  try {
    const res = await getRoute({
      originX: currentLocation.value.lng,
      originY: currentLocation.value.lat,
      destX: selectedPlace.value.x,
      destY: selectedPlace.value.y,
      priority,
    })

    const path = res?.data?.path || []
    if (!path.length) {
      alert("경로를 조회할 수 없습니다")
      return
    }

    routeInfo.value = {
      distanceText: `${(res.data.distance / 1000).toFixed(2)}km`,
      durationText: `${Math.ceil(res.data.duration / 60)}분`,
    }

    drawRoutePolyline(path)
  } catch (err) {
    alert("경로 조회 실패: " + (err.response?.data?.detail || err.message))
  }
}

function onSearch() {
  if (!map || !ps) {
    alert("지도가 준비되지 않았습니다")
    return
  }

  const searchKeyword =
    keyword.value.trim() || `${selectedSido.value} ${selectedSigungu.value} ${selectedBank.value}`

  if (!searchKeyword.trim()) {
    alert("검색어를 입력하세요")
    return
  }

  clearResults()
  const center = map.getCenter()

  ps.keywordSearch(
    searchKeyword,
    (data, status) => {
      if (status === kakaoObj.maps.services.Status.OK) {
        const converted = data.map((place) => ({
          id: place.id || `${place.x}:${place.y}`,
          name: place.place_name,
          address: place.road_address_name || place.address_name,
          x: parseFloat(place.x),
          y: parseFloat(place.y),
          distanceKm: place.distance ? Number(place.distance) / 1000 : null,
        }))

        results.value = converted

        clearMarkers()
        const bounds = new kakaoObj.maps.LatLngBounds()

        converted.forEach((place) => {
          const pos = new kakaoObj.maps.LatLng(place.y, place.x)
          const marker = new kakaoObj.maps.Marker({ map, position: pos })
          markers.push(marker)
          bounds.extend(pos)
          marker.addListener("click", () => selectPlace(place))
        })

        map.setBounds(bounds)
        requestAnimationFrame(() => map && map.relayout())
      } else if (status === kakaoObj.maps.services.Status.ZERO_RESULT) {
        results.value = []
        alert("검색 결과가 없습니다")
      } else {
        alert("검색 중 오류가 발생했습니다")
      }
    },
    { location: center, radius: 5000, sort: kakaoObj.maps.services.SortBy.DISTANCE }
  )
}

onMounted(async () => {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        currentLocation.value = { lat: position.coords.latitude, lng: position.coords.longitude }
      },
      () => {}
    )
  }

  try {
    const resp = await fetch("/data.json")
    const d = await resp.json()
    mapInfo.value = d.mapInfo || []
    bankInfo.value = d.bankInfo || []
  } catch (_) {}

  if (!window.kakao || !window.kakao.maps) {
    alert("카카오 지도 SDK 로드 실패 (index.html 로드/키/플랫폼 등록 확인)")
    return
  }

  kakaoObj = window.kakao

  kakaoObj.maps.load(() => {
    if (!mapEl.value) return
    if (!kakaoObj.maps.services) {
      alert("services 라이브러리가 없습니다. (libraries=services 확인)")
      return
    }

    const initialLat = currentLocation.value?.lat || 37.5665
    const initialLng = currentLocation.value?.lng || 126.978
    const initialPos = new kakaoObj.maps.LatLng(initialLat, initialLng)

    map = new kakaoObj.maps.Map(mapEl.value, { center: initialPos, level: 5 })
    ps = new kakaoObj.maps.services.Places()
    infoWindow = new kakaoObj.maps.InfoWindow({ zIndex: 1 })

    startMarker = new kakaoObj.maps.Marker({ map, position: initialPos })
    const markerLabel = currentLocation.value ? "📍 현재 위치" : "📍 기본 위치(서울시청)"
    startInfo = new kakaoObj.maps.InfoWindow({
      content: `<div style="padding:6px 8px;font-size:12px;"><b>${markerLabel}</b><br/>위도: ${initialLat.toFixed(4)}<br/>경도: ${initialLng.toFixed(4)}</div>`,
    })
    startInfo.open(map, startMarker)

    requestAnimationFrame(() => {
      map.relayout()
      map.setCenter(initialPos)
    })
  })
})

onUnmounted(() => destroyAll())
</script>

<style scoped>
/* ✅ /map main이 높이를 고정해줬기 때문에 여기서는 100%로 채우기만 하면 됨 */
.page {
  height: 100%;
  max-width: 1320px;
  margin: 0 auto;
  padding: 28px 16px 16px;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.page-head {
  margin-bottom: 14px;
}
.page-title {
  font-size: 22px;
  font-weight: 800;
  margin: 0;
}
.page-sub {
  margin: 6px 0 0;
  font-size: 13px;
  color: #6b7280;
}

/* ✅ 남은 영역을 grid가 먹도록 */
.grid {
  flex: 1;
  min-height: 0;

  display: grid;
  grid-template-columns: 360px 1fr;
  gap: 18px;
  align-items: stretch; /* ✅ 두 카드 높이 맞춤 */
}

.card {
  background: #fff;
  border: 1px solid #e9ecef;
  border-radius: 16px;
  box-shadow: 0 10px 26px rgba(16, 24, 40, 0.06);
}

.side-card {
  padding: 18px;
  height: 100%;     /* ✅ 100vh 계산 제거 */
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.card-title {
  font-weight: 800;
  margin: 0 0 10px;
}

.divider {
  height: 1px;
  background: #eef1f3;
  margin: 12px 0;
}

.hint {
  margin-top: 10px;
  font-size: 12px;
  color: #6b7280;
  background: #f8fafc;
  border: 1px solid #eef1f3;
  border-radius: 10px;
  padding: 10px 12px;
}

.result-head {
  margin-top: 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}
.sort {
  width: 120px;
}

.result-list {
  margin-top: 10px;
  overflow-y: auto;
  padding-right: 6px;
  flex: 1;
  min-height: 0;
}

.result-item {
  width: 100%;
  background: #fff;
  border: 1px solid rgba(16, 24, 40, 0.10);
  border-radius: 14px;
  padding: 12px;
  text-align: left;
  transition: transform 0.12s ease, box-shadow 0.12s ease, border-color 0.12s ease;
  margin-bottom: 10px;
}
.result-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 14px 26px rgba(16, 24, 40, 0.08);
}
.result-item.active {
  border-color: #198754;
  box-shadow: 0 14px 28px rgba(25, 135, 84, 0.16);
}

.avatar {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: #eef2ff;
  display: grid;
  place-items: center;
  color: #1d4ed8;
  flex: 0 0 auto;
}

.name {
  font-weight: 800;
  font-size: 14px;
}
.addr {
  font-size: 12px;
  color: #6b7280;
  margin-top: 2px;
}

.dist {
  font-size: 12px;
  color: #6b7280;
}
.more {
  font-size: 12px;
  color: #2563eb;
  margin-top: 6px;
}

.map-card {
  overflow: hidden;
  height: 100%;   /* ✅ 100vh 계산 제거 */
  min-height: 0;
}

.map-card-head {
  padding: 14px 16px;
  font-weight: 800;
  border-bottom: 1px solid #eef1f3;
  background: #ffffff;
}

.map-card-body {
  padding: 14px 16px 16px;
  height: calc(100% - 52px); /* head 높이만큼(대략) */
  min-height: 0;
}

.map-area {
  position: relative;
  border-radius: 14px;
  overflow: hidden;
  border: 1px solid #eef1f3;

  height: 100%;   /* ✅ 100vh 제거 */
  min-height: 0;

  background: linear-gradient(180deg, #fbfaf9 0%, #f7f6f5 100%);
}

.map-canvas {
  width: 100%;
  height: 100%;
}

.route-panel {
  position: absolute;
  top: 12px;
  left: 12px;
  width: 360px;
  max-width: calc(100% - 24px);
  border-radius: 14px;
  z-index: 50;
}

@media (max-width: 992px) {
  .grid {
    grid-template-columns: 1fr;
  }
  .side-card {
    height: auto;
  }
  .map-card {
    height: auto;
  }
  .map-card-body {
    height: auto;
  }
  .map-area {
    height: 56vh;
    min-height: 420px;
  }
}

.result-list::-webkit-scrollbar {
  width: 10px;
}
.result-list::-webkit-scrollbar-thumb {
  background: rgba(16, 24, 40, 0.10);
  border-radius: 8px;
}
</style>
