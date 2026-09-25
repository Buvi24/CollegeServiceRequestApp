// src/pages/AuditLogsPage.jsx
// Shows the system-wide audit log (all requests), newest first.
// Read-only — no create/update/delete, matching the backend design.
import { useEffect, useState } from 'react'
import { getAllAuditLogs } from '../api/client'

export default function AuditLogsPage() {
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getAllAuditLogs().then(setLogs).catch(() => {}).finally(() => setLoading(false))
  }, [])

  return (
    <div>
      <h4>Audit Logs <small className="text-muted fs-6">(all requests, newest first)</small></h4>

      {loading ? <p>Loading…</p> : (
        <table className="table table-sm table-bordered">
          <thead className="table-dark">
            <tr><th>Action</th><th>request ID</th><th>Performed By</th><th>Details</th><th>When</th></tr>
          </thead>
          <tbody>
            {logs.length === 0 && <tr><td colSpan={5} className="text-center text-muted">No audit log entries yet.</td></tr>}
            {logs.map(log => (
              <tr key={log.id}>
                <td><span className="badge bg-info text-dark">{log.action}</span></td>
                <td><code>{log.request_id.slice(0, 8)}…</code></td>
                <td><code>{log.performed_by.slice(0, 8)}…</code></td>
                <td>{log.details}</td>
                <td><small>{new Date(log.created_at).toLocaleString()}</small></td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}