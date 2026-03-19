import { useState, useCallback } from 'react'
import './App.css'

const BASE = (import.meta.env.VITE_API_URL || 'http://localhost:8001') + '/YAAS/content/v1'

// ── Helpers ────────────────────────────────────────────────────

const STAGES = [
  { id: 'ideation',   label: 'Ideation',   num: 1 },
  { id: 'thumbnail',  label: 'Thumbnail',  num: 2 },
  { id: 'script',     label: 'Script',     num: 3 },
  { id: 'video',      label: 'Video',      num: 4 },
  { id: 'seo',        label: 'SEO',        num: 5 },
  { id: 'publish',    label: 'Publish',    num: 6 },
]

const INIT_STATUS = () =>
  Object.fromEntries(STAGES.map(s => [s.id, 'idle']))

async function apiFetch(url, options = {}) {
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  const data = await res.json()
  if (!res.ok) throw new Error(data?.detail || `HTTP ${res.status}`)
  return data
}

// ── Icons ──────────────────────────────────────────────────────

const Icon = {
  Logo: () => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polygon points="23 7 16 12 23 17 23 7"/>
      <rect x="1" y="5" width="15" height="14" rx="2" ry="2"/>
    </svg>
  ),
  Check: () => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="20 6 9 17 4 12"/>
    </svg>
  ),
  X: () => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
    </svg>
  ),
  ChevronDown: () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="6 9 12 15 18 9"/>
    </svg>
  ),
  Play: () => (
    <svg viewBox="0 0 24 24" fill="currentColor">
      <polygon points="5 3 19 12 5 21 5 3"/>
    </svg>
  ),
  Refresh: () => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="23 4 23 10 17 10"/>
      <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
    </svg>
  ),
  Warn: () => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
      <line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
    </svg>
  ),
  Info: () => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10"/>
      <line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
    </svg>
  ),
  Star: () => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
    </svg>
  ),
  Sparkle: () => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 3a1 1 0 0 1 1 1v2a1 1 0 0 1-2 0V4a1 1 0 0 1 1-1zm0 14a1 1 0 0 1 1 1v2a1 1 0 0 1-2 0v-2a1 1 0 0 1 1-1zM3 12a1 1 0 0 1 1-1h2a1 1 0 0 1 0 2H4a1 1 0 0 1-1-1zm14 0a1 1 0 0 1 1-1h2a1 1 0 0 1 0 2h-2a1 1 0 0 1-1-1z"/>
      <circle cx="12" cy="12" r="3"/>
    </svg>
  ),
}

// ── Sub-components ──────────────────────────────────────────────

function StatusPill({ status }) {
  if (status === 'loading') return (
    <span className="card-status-pill pill-loading">
      <span className="btn-spinner" style={{width:10,height:10,borderWidth:1.5}} />
      Running
    </span>
  )
  if (status === 'done') return (
    <span className="card-status-pill pill-done">
      <Icon.Check /> Done
    </span>
  )
  if (status === 'error') return (
    <span className="card-status-pill pill-error">
      <Icon.X /> Error
    </span>
  )
  return <span className="card-status-pill pill-idle">Waiting</span>
}

function AgentCard({ stage, status, open, onToggle, locked, children }) {
  const cardClass = [
    'card',
    status === 'done' ? 'done' : '',
    status === 'error' ? 'error' : '',
    locked ? 'locked' : '',
    !locked && status !== 'done' && status !== 'error' ? 'active' : '',
  ].filter(Boolean).join(' ')

  return (
    <div className={cardClass}>
      <div className="card-header" onClick={onToggle}>
        <div className="card-step-badge">{stage.num}</div>
        <div className="card-title-group">
          <div className="card-title">{stage.label} Agent</div>
          <div className="card-subtitle">
            {locked ? 'Complete previous steps first' : `Step ${stage.num} of 6`}
          </div>
        </div>
        <StatusPill status={status} />
        <span className={`card-chevron ${open ? 'open' : ''}`}>
          <Icon.ChevronDown />
        </span>
      </div>
      {open && !locked && (
        <div className="card-body">
          {children}
        </div>
      )}
    </div>
  )
}

// ── Ideation Panel ──────────────────────────────────────────────

function IdeationPanel({ status, state, onRun }) {
  const [form, setForm] = useState({
    topic: '', audience: '', region: 'Global', content_format: 'short-form',
  })
  const set = (k, v) => setForm(p => ({ ...p, [k]: v }))
  const loading = status === 'loading'

  const ideas = state?.ideas
    ? state.ideas.split(/\n\n+/).filter(Boolean)
    : []

  return (
    <>
      <div className="form-grid">
        <div className="form-group">
          <label className="form-label">Topic <span className="form-required">*</span></label>
          <input className="form-input" placeholder="e.g. AI tools for students"
            value={form.topic} onChange={e => set('topic', e.target.value)}
            disabled={loading} id="ideation-topic" />
        </div>
        <div className="form-group">
          <label className="form-label">Audience <span className="form-required">*</span></label>
          <input className="form-input" placeholder="e.g. college students"
            value={form.audience} onChange={e => set('audience', e.target.value)}
            disabled={loading} id="ideation-audience" />
        </div>
        <div className="form-group">
          <label className="form-label">Region</label>
          <input className="form-input" placeholder="Global"
            value={form.region} onChange={e => set('region', e.target.value)}
            disabled={loading} id="ideation-region" />
        </div>
        <div className="form-group">
          <label className="form-label">Content Format</label>
          <select className="form-select" value={form.content_format}
            onChange={e => set('content_format', e.target.value)}
            disabled={loading} id="ideation-format">
            <option value="short-form">Short-form (Reels / Shorts)</option>
            <option value="long-form">Long-form (Full video)</option>
          </select>
        </div>
      </div>

      <div className="btn-row">
        <button className="btn btn-primary" id="ideation-run"
          disabled={loading || !form.topic.trim() || !form.audience.trim()}
          onClick={() => onRun(form)}>
          {loading ? <><span className="btn-spinner" />Generating Ideas…</> : <><Icon.Play />Generate Ideas</>}
        </button>
      </div>

      {ideas.length > 0 && (
        <div className="output-section">
          <div className="output-label">💡 Generated Ideas</div>
          <div className="ideas-list">
            {ideas.map((idea, i) => (
              <div className="idea-item" key={i}>
                <div className="idea-number">Idea {i + 1}</div>
                <div className="idea-text">{idea.replace(/^\d+\.\s*/, '').trim()}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </>
  )
}

// ── Thumbnail Panel ─────────────────────────────────────────────

function ThumbnailPanel({ status, state, onRun }) {
  const [form, setForm] = useState({
    selected_idea_number: 1,
    enable_image_generation: false,
    image_provider: 'gemini',
    text_render_mode: 'overlay',
  })
  const set = (k, v) => setForm(p => ({ ...p, [k]: v }))
  const loading = status === 'loading'
  const thumb = state?.thumbnail

  const ideaCount = state?.ideas
    ? state.ideas.split(/\n\n+/).filter(Boolean).length
    : 5

  return (
    <>
      <div className="form-grid">
        <div className="form-group">
          <label className="form-label">Select Idea #</label>
          <select className="form-select" value={form.selected_idea_number}
            onChange={e => set('selected_idea_number', Number(e.target.value))}
            disabled={loading} id="thumb-idea-num">
            {Array.from({ length: ideaCount }, (_, i) => (
              <option key={i + 1} value={i + 1}>Idea {i + 1}</option>
            ))}
          </select>
        </div>
        <div className="form-group">
          <label className="form-label">Text Render Mode</label>
          <select className="form-select" value={form.text_render_mode}
            onChange={e => set('text_render_mode', e.target.value)}
            disabled={loading} id="thumb-render-mode">
            <option value="overlay">Overlay</option>
            <option value="embedded">Embedded</option>
          </select>
        </div>
      </div>

      <div className="checkbox-row" style={{ marginTop: '0.75rem' }}>
        <input type="checkbox" id="thumb-gen-img" checked={form.enable_image_generation}
          onChange={e => set('enable_image_generation', e.target.checked)}
          disabled={loading} />
        <label htmlFor="thumb-gen-img">Generate actual thumbnail image (uses Gemini / Stability AI API)</label>
      </div>

      {form.enable_image_generation && (
        <div className="form-grid" style={{ marginTop: '0.75rem' }}>
          <div className="form-group">
            <label className="form-label">Image Provider</label>
            <select className="form-select" value={form.image_provider}
              onChange={e => set('image_provider', e.target.value)}
              disabled={loading} id="thumb-provider">
              <option value="gemini">Gemini</option>
              <option value="stability">Stability AI</option>
            </select>
          </div>
        </div>
      )}

      <div className="btn-row">
        <button className="btn btn-primary" id="thumbnail-run"
          disabled={loading} onClick={() => onRun(form)}>
          {loading ? <><span className="btn-spinner" />Crafting Thumbnail…</> : <><Icon.Star />Generate Thumbnail</>}
        </button>
      </div>

      {thumb && (
        <div className="output-section">
          <div className="output-label">🎨 Thumbnail Spec</div>
          <div className="thumb-grid">
            {thumb.thumbnail_spec && Object.entries(thumb.thumbnail_spec).map(([k, v]) => (
              <div className="thumb-field" key={k}>
                <div className="thumb-field-key">{k.replace(/_/g, ' ')}</div>
                <div className="thumb-field-value">
                  {typeof v === 'object' ? JSON.stringify(v) : String(v)}
                </div>
              </div>
            ))}
            {thumb.thumbnail_text && (
              <div className="thumb-field" style={{ gridColumn: '1 / -1' }}>
                <div className="thumb-field-key">Headline Text</div>
                <div className="thumb-field-value" style={{ fontSize: '1rem', fontWeight: 700 }}>
                  {thumb.thumbnail_text}
                </div>
              </div>
            )}
          </div>
          {thumb.image_base64 && (
            <div className="thumb-image-wrap" style={{ marginTop: '0.75rem' }}>
              <img src={`data:image/png;base64,${thumb.image_base64}`} alt="Generated thumbnail" />
            </div>
          )}
          {!thumb.image_base64 && thumb.image_prompt && (
            <div className="banner banner-info" style={{ marginTop: '0.75rem' }}>
              <Icon.Info />
              <span><strong>Image prompt ready.</strong> Enable image generation above to generate an actual thumbnail image.</span>
            </div>
          )}
        </div>
      )}
    </>
  )
}

// ── Script Panel ────────────────────────────────────────────────

function ScriptPanel({ status, state, onRun }) {
  const loading = status === 'loading'
  const timeline = state?.script_timeline

  return (
    <>
      <div className="banner banner-info">
        <Icon.Info />
        <span>No inputs needed — the script is automatically generated from your selected idea and thumbnail spec.</span>
      </div>

      <div className="btn-row">
        <button className="btn btn-primary" id="script-run"
          disabled={loading} onClick={onRun}>
          {loading
            ? <><span className="btn-spinner" />Writing Script…</>
            : <><Icon.Sparkle />Generate Script</>}
        </button>
      </div>

      {timeline && (
        <div className="output-section">
          {timeline.video_meta && (
            <div className="banner banner-success" style={{ marginBottom: '0.75rem' }}>
              <Icon.Check />
              <span>
                <strong>{timeline.video_meta.title}</strong> —&nbsp;
                {timeline.video_meta.tone} · {timeline.video_meta.duration_seconds}s
              </span>
            </div>
          )}
          <div className="output-label">🎬 Scene Timeline</div>
          <div className="scenes-list">
            {(timeline.timeline || []).map((scene, i) => (
              <div className="scene-card" key={i}>
                <div className="scene-header">
                  <span className="scene-num">Scene {scene.scene_number}</span>
                  <span className="scene-shot">{scene.shot_type}</span>
                </div>
                <div className="scene-visual">{scene.visual_description}</div>
                {scene.voiceover?.text && (
                  <div className="scene-voiceover">"{scene.voiceover.text}"</div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </>
  )
}

// ── Video Panel ─────────────────────────────────────────────────

function VideoPanel({ status, state, onRun }) {
  const [filename, setFilename] = useState('generated_reel.mp4')
  const loading = status === 'loading'

  return (
    <>
      <div className="banner banner-warn">
        <Icon.Warn />
        <span>
          <strong>This step calls Google Veo 3 and may take 1–3 minutes.</strong> Keep this tab open and wait for the spinner to stop.
        </span>
      </div>

      <div className="form-grid" style={{ marginTop: '0.75rem' }}>
        <div className="form-group">
          <label className="form-label">Output Filename</label>
          <input className="form-input" value={filename}
            onChange={e => setFilename(e.target.value)}
            disabled={loading} id="video-filename"
            placeholder="generated_reel.mp4" />
        </div>
      </div>

      <div className="btn-row">
        <button className="btn btn-primary" id="video-run"
          disabled={loading} onClick={() => onRun({ output_filename: filename })}>
          {loading ? <><span className="btn-spinner" />Generating Video…</> : <><Icon.Play />Generate Video</>}
        </button>
      </div>

      {loading && (
        <div className="video-loading-banner">
          <div className="big-spinner" />
          <div className="video-loading-title">Veo 3 is generating your reel…</div>
          <div className="video-loading-sub">This typically takes 1–3 minutes. Please wait.</div>
          <div className="progress-bar-wrap">
            <div className="progress-bar-fill" />
          </div>
        </div>
      )}

      {state?.video_path && !loading && (
        <div className="output-section">
          <div className="output-label">🎥 Generated Video</div>
          {state.video_url ? (
            <video 
              controls 
              src={state.video_url} 
              style={{ width: '100%', borderRadius: 8, marginTop: '0.5rem', background: 'black', maxHeight: 400 }}
            />
          ) : (
            <div className="video-path-box">{state.video_path}</div>
          )}
          <div className="banner banner-success" style={{ marginTop: '0.6rem' }}>
            <Icon.Check />
            <span>Video generated successfully! It is saved at: <br/><code style={{ fontSize: '0.8rem' }}>{state.video_path}</code></span>
          </div>
        </div>
      )}
    </>
  )
}

// ── SEO Panel ───────────────────────────────────────────────────

function SeoPanel({ status, state, onRun }) {
  const loading = status === 'loading'
  const seo = state?.seo_metadata

  return (
    <>
      <div className="banner banner-info">
        <Icon.Info />
        <span>SEO metadata is automatically generated from your script and idea — no inputs needed.</span>
      </div>

      <div className="btn-row">
        <button className="btn btn-primary" id="seo-run"
          disabled={loading} onClick={onRun}>
          {loading ? <><span className="btn-spinner" />Optimising…</> : <><Icon.Star />Generate SEO</>}
        </button>
      </div>

      {seo && (
        <div className="output-section">
          <div className="output-label">🔍 SEO Metadata</div>
          <div className="seo-meta-block">
            <div className="seo-meta-key">Title</div>
            <div className="seo-meta-value" style={{ fontWeight: 700 }}>{seo.title}</div>
          </div>
          <div className="seo-meta-block">
            <div className="seo-meta-key">Description</div>
            <div className="seo-meta-value">{seo.description}</div>
          </div>
          {seo.tags?.length > 0 && (
            <div className="seo-meta-block">
              <div className="seo-meta-key">Tags</div>
              <div className="seo-tags">
                {seo.tags.map((t, i) => (
                  <span className="seo-tag" key={i}>{t}</span>
                ))}
              </div>
            </div>
          )}
          <div style={{ display: 'flex', gap: '0.6rem', flexWrap: 'wrap' }}>
            {seo.privacy && (
              <div className="seo-meta-block" style={{ flex: 1, minWidth: 140 }}>
                <div className="seo-meta-key">Privacy</div>
                <div className="seo-meta-value" style={{ textTransform: 'capitalize' }}>{seo.privacy}</div>
              </div>
            )}
            {seo.scheduled_time && (
              <div className="seo-meta-block" style={{ flex: 2 }}>
                <div className="seo-meta-key">Scheduled Time</div>
                <div className="seo-meta-value">{seo.scheduled_time}</div>
              </div>
            )}
          </div>
        </div>
      )}
    </>
  )
}

// ── Publish Panel ───────────────────────────────────────────────

function PublishPanel({ status, state, error, onRun }) {
  const loading = status === 'loading'
  const pub = state?.publish_response
  const oauthRequired = state?.oauth_required

  return (
    <>
      <div className="banner banner-info" style={{ marginBottom: '1rem' }}>
        <Icon.Info />
        <span>You are ready to publish! Click the button below.</span>
      </div>

      <div className="btn-row">
        <button className="btn btn-primary" id="publish-run"
          disabled={loading} onClick={onRun}>
          {loading
            ? <><span className="btn-spinner" />Publishing…</>
            : <><Icon.Play />Publish to YouTube</>}
        </button>
      </div>

      {oauthRequired && (
        <div className="banner banner-warn" style={{ marginTop: '1rem', display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: '0.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <Icon.Warn />
            <span><strong>Authentication Required:</strong> You need to securely connect your YouTube account to publish.</span>
          </div>
          <button className="btn" style={{ background: 'white', color: 'black', padding: '0.4rem 0.8rem', fontSize: '0.85rem' }}
            onClick={() => window.open(`${BASE}/auth/youtube/login`, 'OAuth', 'width=500,height=700')}>
            Connect YouTube Account
          </button>
        </div>
      )}

      {error && !oauthRequired && (
        <div className="banner banner-error" style={{ marginTop: '1rem' }}>
          <Icon.Warn />
          <span><strong>Publish failed:</strong> {error}</span>
        </div>
      )}

      {pub && !error && (
        <div className="output-section" style={{ marginTop: '1rem' }}>
          <div className="banner banner-success">
            <Icon.Check />
            <span>
              <strong>Published!</strong> YouTube Video ID:&nbsp;
              <a className="youtube-link"
                href={`https://www.youtube.com/watch?v=${pub.id}`}
                target="_blank" rel="noreferrer">
                {pub.id}
              </a>
            </span>
          </div>
          {pub.snippet && (
            <div className="seo-meta-block" style={{ marginTop: '0.6rem' }}>
              <div className="seo-meta-key">Published Title</div>
              <div className="seo-meta-value">{pub.snippet.title}</div>
            </div>
          )}
        </div>
      )}
    </>
  )
}

// ── Analytics Panel ─────────────────────────────────────────────

function AnalyticsPanel() {
  const [videoId, setVideoId] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)

  const handleRun = async () => {
    if (!videoId.trim()) return
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const data = await apiFetch(`${BASE}/analytics`, {
        method: 'POST',
        body: JSON.stringify({ video_id: videoId.trim() }),
      })
      setResult(data.state?.analytics || null)
      if (!data.state?.analytics) {
        setError('No analytics data returned. Make sure the video ID is valid and OAuth completed in the browser popup.')
      }
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const metrics = result?.metrics
  const insights = result?.insights

  const fmtPct = (v) => v != null ? `${(v * 100).toFixed(1)}%` : '—'
  const fmtNum = (v) => v != null ? v.toLocaleString() : '—'

  return (
    <div className="analytics-page">
      <div className="analytics-header">
        <div className="analytics-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/>
            <line x1="6" y1="20" x2="6" y2="14"/>
          </svg>
        </div>
        <div>
          <h2 className="analytics-title">Video Analytics</h2>
          <p className="analytics-subtitle">Analyze any YouTube video's real performance data</p>
        </div>
      </div>

      <div className="banner banner-info" style={{ marginBottom: '1rem' }}>
        <Icon.Info />
        <span>A browser window will open for Google OAuth on first run. Complete the sign-in to grant access to YouTube Analytics.</span>
      </div>

      <div className="form-grid single" style={{ marginTop: 0 }}>
        <div className="form-group">
          <label className="form-label">YouTube Video ID <span className="form-required">*</span></label>
          <input className="form-input" placeholder="e.g. dQw4w9WgXcQ"
            value={videoId} onChange={e => setVideoId(e.target.value)}
            disabled={loading}
            onKeyDown={e => e.key === 'Enter' && handleRun()} />
        </div>
      </div>

      <div className="btn-row">
        <button className="btn btn-primary" disabled={loading || !videoId.trim()} onClick={handleRun}>
          {loading
            ? <><span className="btn-spinner" />Analyzing…</>
            : <><Icon.Star />Analyze Video</>}
        </button>
      </div>

      {error && (
        <div className="banner banner-error" style={{ marginTop: '1rem' }}>
          <Icon.Warn />
          <span><strong>Error:</strong> {error}</span>
        </div>
      )}

      {metrics && (
        <div className="output-section">
          <div className="output-label">Video: {metrics.title || metrics.video_id}</div>

          {/* Key Metrics Grid */}
          <div className="analytics-metrics-grid">
            <div className="analytics-metric-card">
              <div className="analytics-metric-value">{fmtNum(metrics.views)}</div>
              <div className="analytics-metric-label">Views</div>
            </div>
            <div className="analytics-metric-card">
              <div className="analytics-metric-value">{fmtNum(metrics.likes)}</div>
              <div className="analytics-metric-label">Likes</div>
            </div>
            <div className="analytics-metric-card">
              <div className="analytics-metric-value">{fmtNum(metrics.comments)}</div>
              <div className="analytics-metric-label">Comments</div>
            </div>
            <div className="analytics-metric-card">
              <div className="analytics-metric-value">{fmtPct(metrics.engagement_rate)}</div>
              <div className="analytics-metric-label">Engagement Rate</div>
            </div>
            <div className="analytics-metric-card">
              <div className="analytics-metric-value">{fmtNum(Math.round(metrics.watch_time || 0))}</div>
              <div className="analytics-metric-label">Watch Time (min)</div>
            </div>
            <div className="analytics-metric-card">
              <div className="analytics-metric-value">{fmtNum(Math.round(metrics.average_view_duration || 0))}s</div>
              <div className="analytics-metric-label">Avg View Duration</div>
            </div>
          </div>

          {/* Demographics */}
          {metrics.demographics && Object.values(metrics.demographics).some(d => Object.keys(d).length > 0) && (
            <div style={{ marginTop: '1.25rem' }}>
              <div className="output-label">Audience Demographics</div>
              <div className="analytics-demo-grid">
                {metrics.demographics.age && Object.keys(metrics.demographics.age).length > 0 && (
                  <div className="analytics-demo-card">
                    <div className="analytics-demo-title">Age Distribution</div>
                    {Object.entries(metrics.demographics.age)
                      .sort(([, a], [, b]) => b - a)
                      .map(([age, pct]) => (
                      <div className="analytics-bar-row" key={age}>
                        <span className="analytics-bar-label">{age}</span>
                        <div className="analytics-bar-track">
                          <div className="analytics-bar-fill" style={{ width: `${Math.min(pct * 100, 100)}%` }} />
                        </div>
                        <span className="analytics-bar-pct">{fmtPct(pct)}</span>
                      </div>
                    ))}
                  </div>
                )}
                {metrics.demographics.gender && Object.keys(metrics.demographics.gender).length > 0 && (
                  <div className="analytics-demo-card">
                    <div className="analytics-demo-title">Gender Distribution</div>
                    {Object.entries(metrics.demographics.gender)
                      .sort(([, a], [, b]) => b - a)
                      .map(([gender, pct]) => (
                      <div className="analytics-bar-row" key={gender}>
                        <span className="analytics-bar-label">{gender}</span>
                        <div className="analytics-bar-track">
                          <div className="analytics-bar-fill accent2" style={{ width: `${Math.min(pct * 100, 100)}%` }} />
                        </div>
                        <span className="analytics-bar-pct">{fmtPct(pct)}</span>
                      </div>
                    ))}
                  </div>
                )}
                {metrics.demographics.location && Object.keys(metrics.demographics.location).length > 0 && (
                  <div className="analytics-demo-card" style={{ gridColumn: '1 / -1' }}>
                    <div className="analytics-demo-title">Top Locations</div>
                    {Object.entries(metrics.demographics.location)
                      .sort(([, a], [, b]) => b - a)
                      .slice(0, 5)
                      .map(([loc, pct]) => (
                      <div className="analytics-bar-row" key={loc}>
                        <span className="analytics-bar-label">{loc}</span>
                        <div className="analytics-bar-track">
                          <div className="analytics-bar-fill success" style={{ width: `${Math.min(pct * 100, 100)}%` }} />
                        </div>
                        <span className="analytics-bar-pct">{fmtPct(pct)}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Traffic Sources */}
          {metrics.traffic_sources && Object.keys(metrics.traffic_sources).length > 0 && (
            <div style={{ marginTop: '1.25rem' }}>
              <div className="output-label">Traffic Sources</div>
              <div className="analytics-demo-card">
                {Object.entries(metrics.traffic_sources)
                  .sort(([, a], [, b]) => b - a)
                  .map(([source, pct]) => (
                  <div className="analytics-bar-row" key={source}>
                    <span className="analytics-bar-label">{source}</span>
                    <div className="analytics-bar-track">
                      <div className="analytics-bar-fill" style={{ width: `${Math.min(pct * 100, 100)}%` }} />
                    </div>
                    <span className="analytics-bar-pct">{fmtPct(pct)}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Insights */}
          {insights && insights.length > 0 && (
            <div style={{ marginTop: '1.25rem' }}>
              <div className="output-label">Performance Insights</div>
              <div className="analytics-insights-list">
                {insights.map((insight, i) => {
                  const priorityClass = insight.priority === 'high' ? 'insight-high'
                    : insight.priority === 'low' ? 'insight-low' : 'insight-medium'
                  return (
                    <div className={`analytics-insight-card ${priorityClass}`} key={i}>
                      <div className="analytics-insight-header">
                        <span className="analytics-insight-type">{insight.insight_type}</span>
                        <span className={`analytics-insight-priority ${priorityClass}`}>{insight.priority}</span>
                      </div>
                      <div className="analytics-insight-message">{insight.message}</div>
                      {insight.recommendation && (
                        <div className="analytics-insight-rec">{insight.recommendation}</div>
                      )}
                    </div>
                  )
                })}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

// ── Main App ────────────────────────────────────────────────────

export default function App() {
  const [view, setView] = useState('pipeline')  // 'pipeline' | 'analytics'
  const [sessionId, setSessionId] = useState(null)
  const [sessionLoading, setSessionLoading] = useState(false)
  const [globalState, setGlobalState] = useState({})
  const [statuses, setStatuses] = useState(INIT_STATUS())
  const [errors, setErrors] = useState({})
  const [openCard, setOpenCard] = useState(null)

  const setStatus = (id, status) => setStatuses(p => ({ ...p, [id]: status }))
  const setError = (id, msg) => setErrors(p => ({ ...p, [id]: msg }))
  const clearError = id => setErrors(p => ({ ...p, [id]: null }))

  // Is a given stage unlocked?
  const isUnlocked = useCallback((stageId) => {
    const idx = STAGES.findIndex(s => s.id === stageId)
    if (idx === 0) return !!sessionId
    const prev = STAGES[idx - 1]
    return statuses[prev.id] === 'done'
  }, [sessionId, statuses])

  // Create session
  const handleStart = async () => {
    setSessionLoading(true)
    try {
      const data = await apiFetch(`${BASE}/session`, { method: 'POST' })
      setSessionId(data.session_id)
      setGlobalState(data.state || {})
      setStatuses(INIT_STATUS())
      setErrors({})
      setOpenCard('ideation')
    } catch (e) {
      alert(`Failed to create session: ${e.message}`)
    } finally {
      setSessionLoading(false)
    }
  }

  // Reset everything
  const handleReset = () => {
    setSessionId(null)
    setGlobalState({})
    setStatuses(INIT_STATUS())
    setErrors({})
    setOpenCard(null)
  }

  // Generic agent runner
  const runAgent = async (stageId, endpoint, body) => {
    setStatus(stageId, 'loading')
    clearError(stageId)
    try {
      const url = `${BASE}/session/${sessionId}/${endpoint}`
      const options = body
        ? { method: 'POST', body: JSON.stringify(body) }
        : { method: 'POST' }
      const data = await apiFetch(url, options)
      setGlobalState(data.state || {})
      setStatus(stageId, 'done')

      // Auto-open next stage
      const currIdx = STAGES.findIndex(s => s.id === stageId)
      if (currIdx < STAGES.length - 1) {
        setOpenCard(STAGES[currIdx + 1].id)
      }
    } catch (e) {
      setStatus(stageId, 'error')
      setError(stageId, e.message)
    }
  }

  const stageRunners = {
    ideation:  (form) => runAgent('ideation',  'ideation',  form),
    thumbnail: (form) => runAgent('thumbnail', 'thumbnail', form),
    script:    ()     => runAgent('script',    'script',    null),
    video:     (form) => runAgent('video',     'video',     form),
    seo:       ()     => runAgent('seo',       'seo',       null),
    publish:   ()     => runAgent('publish',   'publish',   null),
  }

  const toggleCard = (id) => setOpenCard(p => p === id ? null : id)

  // ── Render ──────────────────────────────────────────────────

  return (
    <div className="app">
      {/* Navbar */}
      <nav className="navbar">
        <div className="navbar-brand">
          <div className="brand-icon"><Icon.Logo /></div>
          <div>
            <div className="brand-name">YAAS</div>
            <div className="brand-tagline">YouTube As A Service</div>
          </div>
        </div>
        <div className="navbar-tabs">
          <button className={`nav-tab ${view === 'pipeline' ? 'active' : ''}`}
            onClick={() => setView('pipeline')}>
            <Icon.Play /> Pipeline
          </button>
          <button className={`nav-tab ${view === 'analytics' ? 'active' : ''}`}
            onClick={() => setView('analytics')}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{width:16,height:16}}>
              <line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/>
              <line x1="6" y1="20" x2="6" y2="14"/>
            </svg>
            Analytics
          </button>
        </div>
        <div className="navbar-meta">
          {view === 'pipeline' && sessionId && (
            <div className="session-badge">
              <span className="session-dot" />
              Session active
            </div>
          )}
          {view === 'pipeline' && sessionId && (
            <button className="btn-reset" onClick={handleReset} id="btn-reset">
              <Icon.Refresh /> Start Over
            </button>
          )}
        </div>
      </nav>

      <div className="main">
        {view === 'pipeline' && (
          <>
            {/* Pipeline Stepper */}
            {sessionId && (
              <div className="stepper">
                {STAGES.map((s, i) => {
                  const st = statuses[s.id]
                  const circleClass = st === 'done' ? 'done' : st === 'error' ? 'error' : openCard === s.id ? 'active' : ''
                  return (
                    <div className="step-item" key={s.id}>
                      <div className="step-circle-wrap">
                        <div className={`step-circle ${circleClass}`}>
                          {st === 'done' ? <Icon.Check /> : st === 'error' ? <Icon.X /> : s.num}
                        </div>
                        <span className={`step-label ${circleClass}`}>{s.label}</span>
                      </div>
                      {i < STAGES.length - 1 && (
                        <div className={`step-connector ${st === 'done' ? 'done' : openCard === s.id ? 'active' : ''}`} />
                      )}
                    </div>
                  )
                })}
              </div>
            )}

            {/* Hero / Start */}
            {!sessionId && (
              <div className="hero">
                <div className="hero-icon"><Icon.Logo /></div>
                <h1 className="hero-title">YouTube As A Service</h1>
                <p className="hero-subtitle">
                  AI-powered pipeline that goes from a single idea to a published YouTube video —
                  Ideation → Thumbnail → Script → Video → SEO → Publish.
                </p>
                <button className="btn-start" onClick={handleStart}
                  disabled={sessionLoading} id="btn-start">
                  {sessionLoading
                    ? <><span className="btn-spinner" style={{ border: '2px solid rgba(255,255,255,0.25)', borderTopColor: 'white' }} />Creating Session…</>
                    : <><Icon.Play />Start New Pipeline</>}
                </button>
              </div>
            )}

            {/* Agent Cards */}
            {sessionId && STAGES.map(stage => {
              const locked = !isUnlocked(stage.id)
              const isOpen = openCard === stage.id

              const panelProps = {
                status: statuses[stage.id],
                state: globalState,
                error: errors[stage.id],
                onRun: stageRunners[stage.id],
              }

              return (
                <AgentCard key={stage.id} stage={stage}
                  status={statuses[stage.id]}
                  open={isOpen} onToggle={() => toggleCard(stage.id)}
                  locked={locked}>
                  {stage.id === 'ideation'   && <IdeationPanel  {...panelProps} />}
                  {stage.id === 'thumbnail'  && <ThumbnailPanel {...panelProps} />}
                  {stage.id === 'script'     && <ScriptPanel    {...panelProps} />}
                  {stage.id === 'video'      && <VideoPanel     {...panelProps} />}
                  {stage.id === 'seo'        && <SeoPanel       {...panelProps} />}
                  {stage.id === 'publish'    && <PublishPanel   {...panelProps} />}

                  {/* Error banner within card */}
                  {errors[stage.id] && stage.id !== 'publish' && (
                    <div className="banner banner-error" style={{ marginTop: '1rem' }}>
                      <Icon.Warn />
                      <span><strong>Error:</strong> {errors[stage.id]}</span>
                    </div>
                  )}
                </AgentCard>
              )
            })}
          </>
        )}

        {view === 'analytics' && <AnalyticsPanel />}
      </div>
    </div>
  )
}
