// src/api/client.js
// Centralised API helper. All fetch calls go through here.
// BASE_URL points to /api which Vite's dev proxy rewrites to http://localhost:8000.
// Change BASE_URL here if the backend moves.

const BASE_URL = '/api'

async function request(method, path, body) {
  const opts = {
    method,
    headers: { 'Content-Type': 'application/json' },
  }
  if (body !== undefined) opts.body = JSON.stringify(body)

  const res = await fetch(`${BASE_URL}${path}`, opts)
  if (res.status === 204) return null   // DELETE returns no body
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail || 'Request failed')
  return data
}

// --- Users ---
export const getUsers = () => request('GET', '/users')
export const createUser = (body) => request('POST', '/users', body)
export const deleteUser = (id) => request('DELETE', `/users/${id}`)

// --- Categories ---
export const getCategories = () => request('GET', '/categories')
export const createCategory = (body) => request('POST', '/categories', body)
export const deleteCategory = (id) => request('DELETE', `/categories/${id}`)

// --- requests ---
export const getrequests = (params = '') => request('GET', `/requests${params}`)
export const getrequest = (id) => request('GET', `/requests/${id}`)
export const createrequest = (body) => request('POST', '/requests', body)
export const deleterequest = (id) => request('DELETE', `/requests/${id}`)
export const assignrequest = (id, body) => request('PATCH', `/requests/${id}/assign`, body)
export const updaterequestStatus = (id, body) => request('PATCH', `/requests/${id}/status`, body)

// --- Comments ---
export const getComments = (requestId) => request('GET', `/requests/${requestId}/comments`)
export const createComment = (requestId, body) => request('POST', `/requests/${requestId}/comments`, body)
export const deleteComment = (requestId, commentId) => request('DELETE', `/requests/${requestId}/comments/${commentId}`)

// --- Attachments ---
export const getAttachments = (requestId) => request('GET', `/requests/${requestId}/attachments`)
export const createAttachment = (requestId, body) => request('POST', `/requests/${requestId}/attachments`, body)
export const deleteAttachment = (requestId, attachmentId) => request('DELETE', `/requests/${requestId}/attachments/${attachmentId}`)

// --- Audit Logs ---
export const getAllAuditLogs = () => request('GET', '/audit-logs')
export const getrequestAuditLogs = (requestId) => request('GET', `/requests/${requestId}/audit-logs`)