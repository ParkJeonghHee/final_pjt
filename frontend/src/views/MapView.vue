<template>
  <div class="page">
    <div class="grid">
      <BankSearchSidebar
        v-model:keyword="keyword"
        v-model:selectedSido="selectedSido"
        v-model:selectedSigungu="selectedSigungu"
        v-model:selectedBank="selectedBank"
        v-model:sortMode="sortMode"
        :sidos="sidos"
        :sigungus="sigungus"
        :banks="banks"
        :results="results"
        :selectedPlace="selectedPlace"
        @search="onSearch"
        @select-place="selectPlace"
        @clear="clearResults"
      />

      <section class="card map-card">
        <div class="map-card-head">은행지도</div>

        <div class="map-card-body">
          <KakaoMapCanvas ref="mapCanvas">
            <RoutePanel
              :place="selectedPlace"
              v-model:mode="routeMode"
              :info="routeInfo"
              @close="selectedPlace = null"
              @search-route="requestRoute"
            />
          </KakaoMapCanvas>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from "vue"
import BankSearchSidebar from "@/components/map/BankSearchSidebar.vue"
import KakaoMapCanvas from "@/components/map/KakaoMapCanvas.vue"
import RoutePanel from "@/components/map/RoutePanel.vue"
import { useKakaoBankMap } from "@/composables/useKakaoBankMap"

const keyword = ref("")
const selectedSido = ref("")
const selectedSigungu = ref("")
const selectedBank = ref("")
const sortMode = ref("distance")

const results = ref([])
const selectedPlace = ref(null)
const routeMode = ref("car")
const routeInfo = ref(null)

const mapInfo = ref([])
const bankInfo = ref([])

const mapCanvas = ref(null)

const {
  currentLocation,
  initMap,
  panTo,
  fitPlaces,
  clearMarkers,
  clearRoute,
  requestRouteTo,
  keywordSearch,
  geocodeAddress,
} = useKakaoBankMap()

const sidos = computed(() => mapInfo.value.map((x) => x.name) || [])
const sigungus = computed(() => {
  const found = mapInfo.value.find((x) => x.name === selectedSido.value)
  return found ? found.countries : []
})
const banks = computed(() => bankInfo.value || [])

watch(selectedSido, () => {
  selectedSigungu.value = ""
  selectedBank.value = ""
})

function convertPlaces(data) {
  return (data || []).map((place) => ({
    id: place.id || `${place.x}:${place.y}`,
    name: place.place_name,
    address: place.road_address_name || place.address_name,
    x: parseFloat(place.x),
    y: parseFloat(place.y),
    distanceKm: place.distance ? Number(place.distance) / 1000 : null,
  }))
}

function clearResults() {
  results.value = []
  selectedPlace.value = null
  routeInfo.value = null
  clearRoute()
  clearMarkers()
}

function selectPlace(place) {
  selectedPlace.value = place
  routeMode.value = "car"
  routeInfo.value = null
  if (place?.x != null && place?.y != null) panTo(place.x, place.y)
}

async function requestRoute() {
  if (!selectedPlace.value) return

  if (routeMode.value === "transit") {
    const url = `https://map.kakao.com/link/to/${encodeURIComponent(selectedPlace.value.name)},${selectedPlace.value.y},${selectedPlace.value.x}`
    window.open(url, "_blank")
    return
  }

  try {
    routeInfo.value = await requestRouteTo(selectedPlace.value)
  } catch (e) {
    alert("경로 조회 실패: " + (e?.message || e))
  }
}

async function getSearchCenterLatLng() {
  const parts = []
  if (selectedSido.value) parts.push(selectedSido.value)
  if (selectedSigungu.value) parts.push(selectedSigungu.value)
  const regionText = parts.join(" ").trim()

  if (regionText) {
    const geo = await geocodeAddress(regionText)
    if (geo) {
      return new window.kakao.maps.LatLng(geo.y, geo.x)
    }
  }
  return null
}

async function onSearch() {
  if (!window.kakao?.maps?.services) {
    alert("카카오 지도 services 라이브러리 확인(libraries=services)")
    return
  }

  const typed = keyword.value.trim()
  const fallbackQuery = `${selectedSido.value} ${selectedSigungu.value} ${selectedBank.value}`.trim()
  const searchKeyword = typed || fallbackQuery
  if (!searchKeyword.trim()) {
    alert("검색어를 입력하세요")
    return
  }

  clearResults()

  const center = await getSearchCenterLatLng()

  let r1 = null
  if (center) {
    r1 = await keywordSearch(searchKeyword, {
      location: center,
      radius: 20000,
      sort: window.kakao.maps.services.SortBy.DISTANCE,
    })
  } else {
    r1 = await keywordSearch(searchKeyword, undefined)
  }

  if (r1.status === window.kakao.maps.services.Status.OK && r1.data?.length) {
    const converted = convertPlaces(r1.data)
    results.value = converted
    fitPlaces(converted, selectPlace)
    return
  }

  const r2 = await keywordSearch(searchKeyword, undefined)
  if (r2.status === window.kakao.maps.services.Status.OK) {
    const converted = convertPlaces(r2.data)
    results.value = converted
    if (converted.length) fitPlaces(converted, selectPlace)
    else alert("검색 결과가 없습니다")
    return
  }

  if (r2.status === window.kakao.maps.services.Status.ZERO_RESULT) {
    alert("검색 결과가 없습니다")
    return
  }

  alert("검색 중 오류가 발생했습니다")
}

onMounted(async () => {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (pos) => (currentLocation.value = { lat: pos.coords.latitude, lng: pos.coords.longitude }),
      () => {}
    )
  }

  try {
    const resp = await fetch("/data.json")
    const d = await resp.json()
    mapInfo.value = d.mapInfo || []
    bankInfo.value = d.bankInfo || []
  } catch (_) {}

  await initMap(mapCanvas.value.el)
})
</script>

<style scoped>
.page {
  height: 100%;
  max-width: 1320px;
  margin: 0 auto;
  padding: 28px 16px 16px;
  display: flex;
  flex-direction: column;
  min-height: 0;
}
.grid {
  flex: 1;
  min-height: 0;
  display: grid;
  grid-template-columns: 360px 1fr;
  gap: 18px;
  align-items: stretch;
}
.card {
  background: #fff;
  border: 1px solid #e9ecef;
  border-radius: 16px;
  box-shadow: 0 10px 26px rgba(16, 24, 40, 0.06);
}
.map-card {
  overflow: hidden;
  height: 100%;
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
  height: calc(100% - 52px);
  min-height: 0;
}
@media (max-width: 992px) {
  .grid { grid-template-columns: 1fr; }
  .map-card-body { height: auto; }
  :deep(.map-area) { height: 56vh; min-height: 420px; }
}
</style>
