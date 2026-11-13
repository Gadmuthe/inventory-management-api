import { useMemo, useState } from 'react'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8002'

export default function App() {
  const [token, setToken] = useState('')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [products, setProducts] = useState([])
  const [form, setForm] = useState({ name: '', category: '', price: '', quantity: '' })
  const [editing, setEditing] = useState(null)
  const [search, setSearch] = useState('')
  const [category, setCategory] = useState('All')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  async function request(path, options = {}) {
    const headers = { ...(options.headers || {}) }
    if (token) headers.Authorization = `Bearer ${token}`
    if (options.body && !(options.body instanceof URLSearchParams)) headers['Content-Type'] = 'application/json'
    const response = await fetch(`${API}${path}`, { ...options, headers })
    const data = response.status === 204 ? null : await response.json().catch(() => ({}))
    if (!response.ok) throw new Error(data.detail || data.message || `Request failed (${response.status})`)
    return data
  }

  async function login(e) {
    e.preventDefault(); setError(''); setBusy(true)
    try {
      const body = new URLSearchParams({ username, password })
      const data = await fetch(`${API}/login`, { method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body }).then(async r => {
        const d = await r.json(); if (!r.ok) throw new Error(d.detail || 'Login failed'); return d
      })
      setToken(data.access_token)
      const headers = { Authorization: `Bearer ${data.access_token}` }
      const r = await fetch(`${API}/products`, { headers })
      const rows = await r.json()
      if (!r.ok) throw new Error(rows.detail || 'Could not load products')
      setProducts(rows)
    } catch (e) { setError(e.message) } finally { setBusy(false) }
  }

  async function refresh() {
    const rows = await request('/products')
    setProducts(rows)
  }

  async function saveProduct(e) {
    e.preventDefault(); setError('')
    const payload = { ...form, price: Number(form.price), quantity: Number(form.quantity) }
    try {
      if (editing) await request(`/products/${editing}`, { method: 'PUT', body: JSON.stringify(payload) })
      else await request('/products', { method: 'POST', body: JSON.stringify(payload) })
      setForm({ name: '', category: '', price: '', quantity: '' }); setEditing(null)
      await refresh()
    } catch (e) { setError(e.message) }
  }

  async function removeProduct(id) {
    if (!window.confirm('Delete this product?')) return
    try { await request(`/products/${id}`, { method: 'DELETE' }); await refresh() }
    catch (e) { setError(e.message) }
  }

  function startEdit(p) {
    setEditing(p.id)
    setForm({ name: p.name, category: p.category, price: String(p.price), quantity: String(p.quantity) })
    document.getElementById('product-form')?.scrollIntoView({ behavior: 'smooth' })
  }

  const categories = ['All', ...new Set(products.map(p => p.category))]
  const shown = useMemo(() => products.filter(p =>
    (p.name.toLowerCase().includes(search.toLowerCase()) || p.category.toLowerCase().includes(search.toLowerCase())) &&
    (category === 'All' || p.category === category)
  ), [products, search, category])
  const stock = products.reduce((s, p) => s + p.quantity, 0)
  const value = products.reduce((s, p) => s + p.price * p.quantity, 0)
  const low = products.filter(p => p.quantity < 10).length

  if (!token) return <main className="login-page"><form className="login-card" onSubmit={login}>
    <div className="brand-mark">IM</div><h1>Inventory Manager</h1><p>Sign in to manage your stock</p>
    {error && <div className="error">{error}</div>}
    <label>Username<input value={username} onChange={e => setUsername(e.target.value)} required /></label>
    <label>Password<input type="password" value={password} onChange={e => setPassword(e.target.value)} required /></label>
    <button className="primary" disabled={busy}>{busy ? 'Signing in…' : 'Sign in'}</button>
  </form></main>

  return <div className="app-shell">
    <aside className="sidebar"><div className="logo"><span>IM</span><b>Inventory</b></div>
      <button className="nav-item active" onClick={() => document.getElementById('products-section')?.scrollIntoView({ behavior: 'smooth' })}>▤ &nbsp; Products</button>
      <div className="sidebar-bottom"><small>INVENTORY MANAGEMENT</small><button className="logout" onClick={() => { setToken(''); setProducts([]) }}>Log out</button></div>
    </aside>
    <main className="main">
      <header className="topbar"><div><span className="eyebrow">OVERVIEW</span><h1>Dashboard</h1></div><span className="user-pill">{username}</span></header>
      {error && <div className="error inline-error">{error}</div>}
      <section className="stats">
        <article className="stat"><span>Total products</span><strong>{products.length}</strong><small>Items in catalogue</small></article>
        <article className="stat"><span>Total stock</span><strong>{stock}</strong><small>Units available</small></article>
        <article className="stat"><span>Low stock</span><strong>{low}</strong><small>Below 10 units</small></article>
        <article className="stat"><span>Inventory value</span><strong>₹{value.toLocaleString('en-IN', { maximumFractionDigits: 2 })}</strong><small>Based on current quantity</small></article>
      </section>
      <section className="panel form-panel" id="product-form"><div className="section-heading"><div><span className="eyebrow">CATALOGUE</span><h2>{editing ? 'Edit product' : 'Add a product'}</h2></div></div>
        <form className="product-form" onSubmit={saveProduct}>
          <label>Product name<input value={form.name} onChange={e => setForm({...form, name:e.target.value})} required /></label>
          <label>Category<input value={form.category} onChange={e => setForm({...form, category:e.target.value})} required /></label>
          <label>Price (₹)<input type="number" min="0.01" step="0.01" value={form.price} onChange={e => setForm({...form, price:e.target.value})} required /></label>
          <label>Quantity<input type="number" min="0" step="1" value={form.quantity} onChange={e => setForm({...form, quantity:e.target.value})} required /></label>
          <div className="form-actions"><button className="primary">{editing ? 'Save changes' : 'Add product'}</button>{editing && <button type="button" className="secondary" onClick={() => {setEditing(null);setForm({name:'',category:'',price:'',quantity:''})}}>Cancel</button>}</div>
        </form>
      </section>
      <section className="panel products" id="products-section"><div className="section-heading"><div><span className="eyebrow">INVENTORY</span><h2>Products</h2></div><span className="count">{shown.length} items</span></div>
        <div className="filters"><input placeholder="Search name or category…" value={search} onChange={e => setSearch(e.target.value)} /><select value={category} onChange={e => setCategory(e.target.value)}>{categories.map(c => <option key={c}>{c}</option>)}</select></div>
        <div className="table-wrap"><table><thead><tr><th>Product</th><th>Category</th><th>Price</th><th>Quantity</th><th>Stock status</th><th>Actions</th></tr></thead>
          <tbody>{shown.map(p => <tr key={p.id}><td><b>{p.name}</b><small>SKU #{p.id}</small></td><td>{p.category}</td><td>₹{Number(p.price).toLocaleString('en-IN')}</td><td>{p.quantity}</td><td><span className={`stock ${p.quantity < 10 ? 'low' : 'good'}`}>{p.quantity < 10 ? 'Low stock' : 'In stock'}</span></td><td><div className="actions"><button className="edit" onClick={() => startEdit(p)}>Edit</button><button className="delete" onClick={() => removeProduct(p.id)}>Delete</button></div></td></tr>)}
          {!shown.length && <tr><td colSpan="6" className="empty">No products found. Add a product above.</td></tr>}</tbody>
        </table></div>
      </section>
      <footer>Inventory Management System · Built with React, FastAPI and PostgreSQL</footer>
    </main>
  </div>
}
