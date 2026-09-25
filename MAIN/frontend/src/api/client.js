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

// --- Tickets ---
export const getTickets = (params = '') => request('GET', `/tickets${params}`)
export const getTicket = (id) => request('GET', `/tickets/${id}`)
export const createTicket = (body) => request('POST', '/tickets', body)
export const deleteTicket = (id) => request('DELETE', `/tickets/${id}`)
export const assignTicket = (id, body) => request('PATCH', `/tickets/${id}/assign`, body)
export const updateTicketStatus = (id, body) => request('PATCH', `/tickets/${id}/status`, body)

// --- Comments ---
export const getComments = (ticketId) => request('GET', `/tickets/${ticketId}/comments`)
export const createComment = (ticketId, body) => request('POST', `/tickets/${ticketId}/comments`, body)
export const deleteComment = (ticketId, commentId) => request('DELETE', `/tickets/${ticketId}/comments/${commentId}`)

// --- Attachments ---
export const getAttachments = (ticketId) => request('GET', `/tickets/${ticketId}/attachments`)
export const createAttachment = (ticketId, body) => request('POST', `/tickets/${ticketId}/attachments`, body)
export const deleteAttachment = (ticketId, attachmentId) => request('DELETE', `/tickets/${ticketId}/attachments/${attachmentId}`)

// --- Audit Logs ---
export const getAllAuditLogs = () => request('GET', '/audit-logs')
export const getTicketAuditLogs = (ticketId) => request('GET', `/tickets/${ticketId}/audit-logs`)