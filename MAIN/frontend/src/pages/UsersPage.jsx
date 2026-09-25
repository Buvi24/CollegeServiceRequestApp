// src/pages/UsersPage.jsx
// Lists all users and provides a form to create a new user.
// Supports deleting a user by clicking the Delete button in the table.
import { useEffect, useState } from 'react'
import { getUsers, createUser, deleteUser } from '../api/client'

const ROLES = ['student', 'faculty', 'service_staff','service_lead', 'admin']

const blank = { name: '', email: '', password: '', role: 'Student' }

export default function UsersPage() {
  const [users, setUsers] = useState([])
  const [form, setForm] = useState(blank)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  const load = () => getUsers().then(setUsers).catch(() => {}).finally(() => setLoading(false))
  useEffect(() => { load() }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      await createUser(form)
      setForm(blank)
      load()
    } catch (err) {
      setError(err.message)
    }
  }

  const handleDelete = async (id) => {
    if (!confirm('Delete this user?')) return
    try { await deleteUser(id); load() } catch (err) { setError(err.message) }
  }

  return (
    <div>
      <h4>Users</h4>

      {/* Create user form */}
      <form onSubmit={handleSubmit} className="row g-2 mb-4">
        <div className="col-md-3">
          <input className="form-control form-control-sm" placeholder="Name" required
            value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} />
        </div>
        <div className="col-md-3">
          <input type="email" className="form-control form-control-sm" placeholder="Email" required
            value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} />
        </div>
        <div className="col-md-2">
          <input type="password" className="form-control form-control-sm" placeholder="Password (min 8)" required minLength={8}
            value={form.password} onChange={e => setForm({ ...form, password: e.target.value })} />
        </div>
        <div className="col-md-2">
          <select className="form-select form-select-sm" value={form.role}
            onChange={e => setForm({ ...form, role: e.target.value })}>
            {ROLES.map(r => <option key={r} value={r}>{r}</option>)}
          </select>
        </div>
        <div className="col-md-2">
          <button className="btn btn-sm btn-primary w-100" type="submit">Add User</button>
        </div>
        {error && <div className="col-12"><small className="text-danger">{error}</small></div>}
      </form>

      {/* Users table */}
      {loading ? <p>Loading…</p> : (
        <table className="table table-sm table-bordered">
          <thead className="table-dark">
            <tr><th>Name</th><th>Email</th><th>Role</th><th>Created</th><th></th></tr>
          </thead>
          <tbody>
            {users.length === 0 && <tr><td colSpan={5} className="text-center text-muted">No users yet.</td></tr>}
            {users.map(u => (
              <tr key={u.id}>
                <td>{u.name}</td>
                <td>{u.email}</td>
                <td><span className="badge bg-secondary">{u.role}</span></td>
                <td>{new Date(u.created_at).toLocaleDateString()}</td>
                <td>
                  <button className="btn btn-sm btn-outline-danger" onClick={() => handleDelete(u.id)}>Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}