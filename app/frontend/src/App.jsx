import React, { useState, useEffect, useCallback } from 'react'

const API = '/api'

const STYLE_ICONS = {
  white_bg: '⬜',
  studio: '💡',
  lifestyle: '🏠',
  outdoor: '🌿',
  automotive: '🏎️',
}

export default function App() {
  const [desc, setDesc] = useState('')
  const [style, setStyle] = useState('white_bg')
  const [seed, setSeed] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [history, setHistory] = useState([])
  const [comfyStatus, setComfyStatus] = useState('checking')
  const [styles, setStyles] = useState({})

  useEffect(() => {
    fetch(`${API}/styles`).then(r => r.json()).then(setStyles).catch(() => {})
    fetchStatus()
    fetchHistory()
  }, [])

  const fetchStatus = () => {
    fetch(`${API}/health`)
      .then(r => r.json())
      .then(d => setComfyStatus(d.comfyui_running ? 'online' : 'offline'))
      .catch(() => setComfyStatus('offline'))
  }

  const fetchHistory = () => {
    fetch(`${API}/history?limit=30`)
      .then(r => r.json())
      .then(d => setHistory(d.images || []))
      .catch(() => {})
  }

  const handleGenerate = async () => {
    if (!desc.trim()) return
    setLoading(true)
    setError('')
    setResult(null)

    try {
      const body = { description: desc.trim(), style }
      if (seed) body.seed = parseInt(seed)

      const res = await fetch(`${API}/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })

      const data = await res.json()
      if (!res.ok) {
        setError(data.detail || 'Generation failed')
      } else {
        setResult(data)
        fetchHistory()
      }
    } catch (e) {
      setError('Failed to connect to API. Is the backend running?')
    }
    setLoading(false)
  }

  const handleRandomSeed = () => {
    setSeed(Math.floor(Math.random() * 999999999).toString())
  }

  const handleHistoryClick = (item) => {
    setResult({
      image_url: item.url,
      style: item.style,
      seed: item.seed,
      elapsed_s: item.elapsed_s,
      description: item.description,
    })
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const handleDownload = (url, filename) => {
    const a = document.createElement('a')
    a.href = url
    a.download = filename || 'aether-image.png'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
  }

  const formatTime = (ts) => {
    const d = new Date(ts * 1000)
    return d.toLocaleString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
  }

  const styleEntries = Object.entries(STYLE_ICONS)

  return (
    <>
      <header className="app-header">
        <div>
          <span className="logo">AETHER</span>
          <span className="logo-sub">dashboard</span>
        </div>
        <div className="header-stats">
          <span>
            <span className={`status-dot ${comfyStatus}`}></span>
            ComfyUI {comfyStatus === 'online' ? 'Ready' : 'Offline'}
          </span>
          {result && <span>Last: {result.elapsed_s}s</span>}
        </div>
      </header>

      <main className="app-main">
        {/* Generator Panel */}
        <div className="generator-panel">
          <h1>Generate Product Photo</h1>
          <p className="panel-subtitle">Describe your product and choose a photography style</p>

          {error && <div className="error-bar">{error}</div>}

          <div className="form-group">
            <label className="form-label">Product Description</label>
            <textarea
              className="form-input"
              placeholder="e.g. A matte black wireless mechanical keyboard with RGB backlighting, aluminum frame..."
              value={desc}
              onChange={e => setDesc(e.target.value)}
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label className="form-label">Photography Style</label>
            <div className="style-grid">
              {Object.entries(styles).map(([key, info]) => (
                <div
                  key={key}
                  className={`style-card ${style === key ? 'active' : ''}`}
                  onClick={() => setStyle(key)}
                >
                  <div className="style-icon">{STYLE_ICONS[key] || '📷'}</div>
                  <div className="style-name">{info.label}</div>
                  <div className="style-desc">{info.desc}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Seed (optional)</label>
            <div className="seed-row">
              <input
                type="number"
                placeholder="Random"
                value={seed}
                onChange={e => setSeed(e.target.value)}
                disabled={loading}
                min="1"
              />
              <button className="seed-random-btn" onClick={handleRandomSeed} disabled={loading}>
                🎲 Random
              </button>
            </div>
          </div>

          <button
            className={`generate-btn ${loading ? 'loading' : ''}`}
            onClick={handleGenerate}
            disabled={loading || !desc.trim()}
          >
            {loading ? (
              <><span className="spinner"></span> Generating...</>
            ) : (
              <>Generate Photo</>
            )}
          </button>

          {/* Result */}
          {loading && !result && (
            <div className="image-result">
              <h3>Generating <span className="result-stats">~15s with Flux 2 Klein</span></h3>
              <div className="skeleton" style={{ aspectRatio: '1', width: '100%' }}></div>
            </div>
          )}

          {result && (
            <div className="image-result">
              <h3>
                Result {result.style && <span className="badge">{STYLE_ICONS[result.style]} {styles[result.style]?.label || result.style}</span>}
                <span className="result-stats">{result.elapsed_s}s | seed {result.seed}</span>
              </h3>
              <div className="image-container">
                <img src={result.image_url} alt="Generated product photo" />
                <button
                  className="download-btn"
                  onClick={() => handleDownload(result.image_url, `aether-${result.style}-${result.seed}.png`)}
                >
                  ⬇ Download
                </button>
              </div>
            </div>
          )}
        </div>

        {/* History Sidebar */}
        <div className="history-panel">
          <h2>
            Gallery
            <span className="history-count">{history.length} images</span>
          </h2>
          <div className="history-list">
            {history.length === 0 && (
              <div className="history-empty">
                <div className="empty-icon">🖼️</div>
                <div>No generated images yet</div>
                <div style={{ fontSize: 11, marginTop: 4, opacity: 0.7 }}>Generate your first product photo above</div>
              </div>
            )}
            {history.map((item) => (
              <div key={item.filename} className="history-item" onClick={() => handleHistoryClick(item)}>
                <img className="history-thumb" src={item.url} alt="Generated" />
                <div className="history-info">
                  <div className="prompt">{item.filename}</div>
                  <div className="history-meta">
                    <span>{item.size_kb} KB</span>
                    <span>{formatTime(item.created)}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>
    </>
  )
}
