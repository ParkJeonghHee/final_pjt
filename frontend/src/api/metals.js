import http from '@/api/http'

export function fetchMetalSeries({ asset = "gold", start = "", end = ""}) {
    const params = { asset }
    if (start) params.start = start
    if (end) params.end = end
    return http.get('/api/metals/series/', { params })
}