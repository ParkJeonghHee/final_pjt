import axios from "axios"

const YT_BASE = "https://www.googleapis.com/youtube/v3"
const API_KEY = import.meta.env.VITE_YOUTUBE_API_KEY

export async function searchYoutubeVideos(query) {
    return axios.get(`${YT_BASE}/search`, {
        params: {
            key: API_KEY,
            part: "snippet",
            type: "video",
            q: query,
            maxResults: 12,
        },
    })
}

export async function fetchYoutubeVideoDetail(videoId) {
    return axios.get(`${YT_BASE}/videos`, {
        params: {
            key: API_KEY,
            part: "snippet",
            id: videoId,
        },
    })
}