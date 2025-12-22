import { defineStore } from 'pinia'

const KEY = 'saved_videos_v1'

function load() {
  try {
    return JSON.parse(localStorage.getItem(KEY) || '[]')
  } catch {
    return []
  }
}
function save(list) {
  localStorage.setItem(KEY, JSON.stringify(list))
}

export const useSavedVideosStore = defineStore('savedVideos', {
  state: () => ({ list: load() }),
  actions: {
    isSaved(id) {
      return this.list.some(v => v.id === id)
    },
    add(video) {
      if (this.isSaved(video.id)) return
      this.list.unshift(video)
      save(this.list)
    },
    remove(id) {
      this.list = this.list.filter(v => v.id !== id)
      save(this.list)
    },
  },
})
