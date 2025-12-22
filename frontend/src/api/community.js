import http from "@/api/http"

// 게시글
export const fetchPosts = (sort = "latest") => 
    http.get("/api/community/posts/", { params: {sort}})

export const fetchPostDetail = (id, sort = "latest") =>
  http.get(`/api/community/posts/${id}/`, {
    params: { sort },
  })

export const togglePostLike = (postId) =>
  http.post(`/api/community/posts/${postId}/like/`)


export const createPost = (payload) => http.post("/api/community/posts/", payload)

export const updatePost = (id, payload) =>
  http.put(`/api/community/posts/${id}/`, payload)

export const deletePost = (id) => http.delete(`/api/community/posts/${id}/`)

// 댓글
export const createComment = (postId, payload) =>
  http.post(`/api/community/posts/${postId}/comments/`, payload)

export const updateComment = (commentId, payload) =>
  http.put(`/api/community/comments/${commentId}/`, payload)

export const deleteComment = (commentId) =>
  http.delete(`/api/community/comments/${commentId}/`)

export const toggleCommentLike = (commentId) =>
  http.post(`/api/community/comments/${commentId}/like/`)
