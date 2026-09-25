// src/pages/requestDetailPage.jsx
// Detail view for a single request. Shows request info, and lets you:
//   - Assign a technician (assigned_to + assigned_by)
//   - Change status (new status + changed_by)
//   - Add / delete comments
//   - Add / delete attachments (metadata only)
//   - View the request's audit log
import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  getrequest, getUsers,
  assignrequest, updaterequestStatus,
  getComments, createComment, deleteComment,
  getAttachments, createAttachment, deleteAttachment,
  getrequestAuditLogs,
} from '../api/client'

const NEXT_STATUSES = {
  new: ['assigned'],
  assigned: ['in_progress'],
  in_progress: ['on_hold', 'resolved'],
  on_hold: ['in_progress'],
  resolved: ['closed'],
  closed: [],
}

const STATUS_COLORS = {
  new: 'secondary', assigned: 'primary', in_progress: 'info',
  on_hold: 'warning', resolved: 'success', closed: 'dark',
}

export default function requestDetailPage() {
  const { requestId } = useParams()
  const navigate = useNavigate()

  const [request, setrequest] = useState(null)
  const [users, setUsers] = useState([])
  const [comments, setComments] = useState([])
  const [attachments, setAttachments] = useState([])
  const [auditLogs, setAuditLogs] = useState([])
  const [error, setError] = useState('')

  // Assign form state
  const [assignTo, setAssignTo] = useState('')
  const [assignBy, setAssignBy] = useState('')

  // Status form state
  const [newStatus, setNewStatus] = useState('')
  const [changedBy, setChangedBy] = useState('')

  // Comment form state
  const [commentContent, setCommentContent] = useState('')
  const [commentAuthor, setCommentAuthor] = useState('')

  // Attachment form state
  const [attForm, setAttForm] = useState({ filename: '', url: '', size: '', uploaded_by: '' })

  const loadAll = () => {
    getrequest(requestId).then(setrequest).catch(() => navigate('/requests'))
    getComments(requestId).then(setComments).catch(() => {})
    getAttachments(requestId).then(setAttachments).catch(() => {})
    getrequestAuditLogs(requestId).then(setAuditLogs).catch(() => {})
  }

  useEffect(() => {
    loadAll()
    getUsers().then(setUsers).catch(() => {})
  }, [requestId])

  const withError = (fn) => async (...args) => {
    setError('')
    try { await fn(...args); loadAll() } catch (e) { setError(e.message) }
  }

  const handleAssign = withError(async (e) => {
    e.preventDefault()
    await assignrequest(requestId, { assigned_to: assignTo, assigned_by: assignBy })
    setAssignTo(''); setAssignBy('')
  })

  const handleStatus = withError(async (e) => {
    e.preventDefault()
    await updaterequestStatus(requestId, { status: newStatus, changed_by: changedBy })
    setNewStatus(''); setChangedBy('')
  })

  const handleComment = withError(async (e) => {
    e.preventDefault()
    await createComment(requestId, { author_id: commentAuthor, content: commentContent })
    setCommentContent(''); setCommentAuthor('')
  })

  const handleDeleteComment = withError(async (commentId) => {
    if (!confirm('Delete comment?')) return
    await deleteComment(requestId, commentId)
  })

  const handleAttachment = withError(async (e) => {
    e.preventDefault()
    await createAttachment(requestId, { ...attForm, size: parseInt(attForm.size, 10) })
    setAttForm({ filename: '', url: '', size: '', uploaded_by: '' })
  })

  const handleDeleteAttachment = withError(async (attachmentId) => {
    if (!confirm('Delete attachment?')) return
    await deleteAttachment(requestId, attachmentId)
  })

  if (!request) return <p>Loading…</p>

  const nextStatuses = NEXT_STATUSES[request.status] || []

  return (
    <div>
      <button className="btn btn-sm btn-outline-secondary mb-3" onClick={() => navigate('/requests')}>
        ← Back to requests
      </button>

      {error && <div className="alert alert-danger py-2">{error}</div>}

      {/* request header */}
      <div className="card mb-3">
        <div className="card-body">
          <h5 className="card-title">{request.title}</h5>
          <p className="card-text text-muted">{request.description}</p>
          <span className={`badge bg-${STATUS_COLORS[request.status] || 'secondary'} me-2`}>{request.status}</span>
          <small className="text-muted">
            Created: {new Date(request.created_at).toLocaleString()} &nbsp;|&nbsp;
            Updated: {new Date(request.updated_at).toLocaleString()}
          </small>
          <br />
          <small className="text-muted">
            Assigned to: {request.assigned_to
              ? (users.find(u => u.id === request.assigned_to)?.name || request.assigned_to)
              : <em>unassigned</em>}
          </small>
        </div>
      </div>

      <div className="row g-3">
        {/* Assign technician */}
        <div className="col-md-6">
          <div className="card">
            <div className="card-header">Assign Technician</div>
            <div className="card-body">
              <form onSubmit={handleAssign} className="row g-2">
                <div className="col-6">
                  <select className="form-select form-select-sm" required value={assignTo}
                    onChange={e => setAssignTo(e.target.value)}>
                    <option value="">-- Assign To --</option>
                    {users.map(u => <option key={u.id} value={u.id}>{u.name} ({u.role})</option>)}
                  </select>
                </div>
                <div className="col-6">
                  <select className="form-select form-select-sm" required value={assignBy}
                    onChange={e => setAssignBy(e.target.value)}>
                    <option value="">-- Assigned By --</option>
                    {users.map(u => <option key={u.id} value={u.id}>{u.name} ({u.role})</option>)}
                  </select>
                </div>
                <div className="col-12">
                  <button className="btn btn-sm btn-primary" type="submit">Assign</button>
                </div>
              </form>
            </div>
          </div>
        </div>

        {/* Change status */}
        <div className="col-md-6">
          <div className="card">
            <div className="card-header">Change Status</div>
            <div className="card-body">
              {nextStatuses.length === 0
                ? <p className="text-muted mb-0">request is <strong>{request.status}</strong> — no further transitions.</p>
                : (
                  <form onSubmit={handleStatus} className="row g-2">
                    <div className="col-6">
                      <select className="form-select form-select-sm" required value={newStatus}
                        onChange={e => setNewStatus(e.target.value)}>
                        <option value="">-- New Status --</option>
                        {nextStatuses.map(s => <option key={s} value={s}>{s}</option>)}
                      </select>
                    </div>
                    <div className="col-6">
                      <select className="form-select form-select-sm" required value={changedBy}
                        onChange={e => setChangedBy(e.target.value)}>
                        <option value="">-- Changed By --</option>
                        {users.map(u => <option key={u.id} value={u.id}>{u.name}</option>)}
                      </select>
                    </div>
                    <div className="col-12">
                      <button className="btn btn-sm btn-warning" type="submit">Update Status</button>
                    </div>
                  </form>
                )}
            </div>
          </div>
        </div>

        {/* Comments */}
        <div className="col-md-6">
          <div className="card">
            <div className="card-header">Comments</div>
            <div className="card-body">
              <form onSubmit={handleComment} className="row g-2 mb-3">
                <div className="col-5">
                  <select className="form-select form-select-sm" required value={commentAuthor}
                    onChange={e => setCommentAuthor(e.target.value)}>
                    <option value="">-- Author --</option>
                    {users.map(u => <option key={u.id} value={u.id}>{u.name}</option>)}
                  </select>
                </div>
                <div className="col-5">
                  <input className="form-control form-control-sm" placeholder="Comment text" required
                    value={commentContent} onChange={e => setCommentContent(e.target.value)} />
                </div>
                <div className="col-2">
                  <button className="btn btn-sm btn-primary w-100" type="submit">Add</button>
                </div>
              </form>
              {comments.length === 0 && <p className="text-muted mb-0">No comments yet.</p>}
              {comments.map(c => (
                <div key={c.id} className="d-flex justify-content-between align-items-start border-bottom py-1">
                  <div>
                    <small className="fw-bold">{users.find(u => u.id === c.author_id)?.name || c.author_id}</small>
                    <small className="text-muted ms-2">{new Date(c.created_at).toLocaleString()}</small>
                    <p className="mb-0">{c.content}</p>
                  </div>
                  <button className="btn btn-sm btn-outline-danger ms-2" onClick={() => handleDeleteComment(c.id)}>×</button>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Attachments */}
        <div className="col-md-6">
          <div className="card">
            <div className="card-header">Attachments (metadata only)</div>
            <div className="card-body">
              <form onSubmit={handleAttachment} className="row g-2 mb-3">
                <div className="col-6">
                  <input className="form-control form-control-sm" placeholder="Filename" required
                    value={attForm.filename} onChange={e => setAttForm({ ...attForm, filename: e.target.value })} />
                </div>
                <div className="col-6">
                  <input className="form-control form-control-sm" placeholder="URL (https://...)" required
                    value={attForm.url} onChange={e => setAttForm({ ...attForm, url: e.target.value })} />
                </div>
                <div className="col-4">
                  <input type="number" className="form-control form-control-sm" placeholder="Size (bytes)" required min={1}
                    value={attForm.size} onChange={e => setAttForm({ ...attForm, size: e.target.value })} />
                </div>
                <div className="col-5">
                  <select className="form-select form-select-sm" required value={attForm.uploaded_by}
                    onChange={e => setAttForm({ ...attForm, uploaded_by: e.target.value })}>
                    <option value="">-- Uploaded By --</option>
                    {users.map(u => <option key={u.id} value={u.id}>{u.name}</option>)}
                  </select>
                </div>
                <div className="col-3">
                  <button className="btn btn-sm btn-primary w-100" type="submit">Add</button>
                </div>
              </form>
              {attachments.length === 0 && <p className="text-muted mb-0">No attachments yet.</p>}
              {attachments.map(a => (
                <div key={a.id} className="d-flex justify-content-between align-items-center border-bottom py-1">
                  <div>
                    <a href={a.url} target="_blank" rel="noreferrer">{a.filename}</a>
                    <small className="text-muted ms-2">({a.size} bytes)</small>
                  </div>
                  <button className="btn btn-sm btn-outline-danger ms-2" onClick={() => handleDeleteAttachment(a.id)}>×</button>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Audit log for this request */}
        <div className="col-12">
          <div className="card">
            <div className="card-header">Audit Log</div>
            <div className="card-body p-0">
              {auditLogs.length === 0 ? <p className="p-3 mb-0 text-muted">No audit entries yet.</p> : (
                <table className="table table-sm mb-0">
                  <thead className="table-light">
                    <tr><th>Action</th><th>Performed By</th><th>Details</th><th>When</th></tr>
                  </thead>
                  <tbody>
                    {auditLogs.map(log => (
                      <tr key={log.id}>
                        <td><span className="badge bg-info text-dark">{log.action}</span></td>
                        <td>{users.find(u => u.id === log.performed_by)?.name || log.performed_by}</td>
                        <td>{log.details}</td>
                        <td><small>{new Date(log.created_at).toLocaleString()}</small></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}