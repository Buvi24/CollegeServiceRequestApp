// src/pages/CategoriesPage.jsx
// Lists all categories and provides a form to create a new one.
// Supports deleting a category.
import { useEffect, useState } from 'react'
import { getCategories, createCategory, deleteCategory } from '../api/client'

const blank = { name: '', description: '' }

export default function CategoriesPage() {
  const [categories, setCategories] = useState([])
  const [form, setForm] = useState(blank)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  const load = () => getCategories().then(setCategories).catch(() => {}).finally(() => setLoading(false))
  useEffect(() => { load() }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      await createCategory(form)
      setForm(blank)
      load()
    } catch (err) {
      setError(err.message)
    }
  }

  const handleDelete = async (id) => {
    if (!confirm('Delete this category?')) return
    try { await deleteCategory(id); load() } catch (err) { setError(err.message) }
  }

  return (
    <div>
      <h4>Categories</h4>

      {/* Create category form */}
      <form onSubmit={handleSubmit} className="row g-2 mb-4">
        <div className="col-md-3">
          <input className="form-control form-control-sm" placeholder="Name" required minLength={2}
            value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} />
        </div>
        <div className="col-md-5">
          <input className="form-control form-control-sm" placeholder="Description (optional)"
            value={form.description} onChange={e => setForm({ ...form, description: e.target.value })} />
        </div>
        <div className="col-md-2">
          <button className="btn btn-sm btn-primary w-100" type="submit">Add Category</button>
        </div>
        {error && <div className="col-12"><small className="text-danger">{error}</small></div>}
      </form>

      {/* Categories table */}
      {loading ? <p>Loading…</p> : (
        <table className="table table-sm table-bordered">
          <thead className="table-dark">
            <tr><th>Name</th><th>Description</th><th>Created</th><th></th></tr>
          </thead>
          <tbody>
            {categories.length === 0 && <tr><td colSpan={4} className="text-center text-muted">No categories yet.</td></tr>}
            {categories.map(c => (
              <tr key={c.id}>
                <td>{c.name}</td>
                <td>{c.description || <span className="text-muted">—</span>}</td>
                <td>{new Date(c.created_at).toLocaleDateString()}</td>
                <td>
                  <button className="btn btn-sm btn-outline-danger" onClick={() => handleDelete(c.id)}>Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}