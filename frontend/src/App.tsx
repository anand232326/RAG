import { useEffect, useRef, useState, type ChangeEvent, type DragEvent, type FormEvent } from 'react'
import './App.css'

type Metric = {
  id: number
  company: string
  year: string
  revenue: string | null
  net_income: string | null
  operating_income: string | null
  cash_flow: string | null
  total_assets: string | null
  total_liabilities: string | null
  risk_factors: string | null
  growth_drivers: string | null
  created_at: string
}

type Message = {
  role: 'assistant' | 'user'
  content: string
}

type IconName = 'grid' | 'file' | 'chat' | 'settings' | 'search' | 'bell' | 'plus' | 'arrow' | 'trend' | 'chart' | 'shield' | 'spark' | 'upload' | 'send' | 'close' | 'check' | 'refresh'

const iconPaths: Record<IconName, string> = {
  grid: 'M3 3h7v7H3z M14 3h7v7h-7z M14 14h7v7h-7z M3 14h7v7H3z',
  file: 'M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z M14 2v6h6 M8 13h8 M8 17h8',
  chat: 'M21 11.5a8.4 8.4 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.4 8.4 0 0 1-3.8-.9L3 21l1.9-5.7a8.4 8.4 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.4 8.4 0 0 1 3.8-.9h.5a8.5 8.5 0 0 1 8 8z',
  settings: 'M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8z M19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1-1.6 2.8-.2-.1a1.7 1.7 0 0 0-1.8.2l-.2.1h-3.2l-.1-.2a1.7 1.7 0 0 0-1.5-1 1.7 1.7 0 0 0-1.1.4l-.2.1-2.8-1.6.1-.2a1.7 1.7 0 0 0-.2-1.8l-.1-.2v-3.2l.2-.1a1.7 1.7 0 0 0 .6-2.6l-.1-.2 1.6-2.8.2.1a1.7 1.7 0 0 0 1.8-.2l.2-.1h3.2l.1.2a1.7 1.7 0 0 0 2.6.6l.2-.1 2.8 1.6-.1.2a1.7 1.7 0 0 0 .2 1.8l.1.2v3.2z',
  search: 'm21 21-4.3-4.3 M19 10.5a8.5 8.5 0 1 1-17 0 8.5 8.5 0 0 1 17 0z',
  bell: 'M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9 M10 21h4',
  plus: 'M12 5v14 M5 12h14',
  arrow: 'M7 17 17 7 M7 7h10v10',
  trend: 'm3 17 6-6 4 4 8-8 M15 7h6v6',
  chart: 'M3 3v18h18 M18 17V9 M13 17V5 M8 17v-3',
  shield: 'M12 22s8-4 8-11V5l-8-3-8 3v6c0 7 8 11 8 11z M9 12l2 2 4-4',
  spark: 'm12 3 1.9 5.8L20 11l-6.1 2.2L12 19l-1.9-5.8L4 11l6.1-2.2L12 3z M19 14l1.2 2.8L23 18l-2.8 1.2L19 22l-1.2-2.8L15 18l2.8-1.2L19 14z',
  upload: 'M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4 M17 8l-5-5-5 5 M12 3v12',
  send: 'm22 2-7 20-4-9-9-4z M22 2 11 13',
  close: 'M18 6 6 18 M6 6l12 12',
  check: 'm5 12 4 4L19 6',
  refresh: 'M20 7v5h-5 M4 17v-5h5 M5.6 9a7 7 0 0 1 11.5-2L20 12 M4 12l2.9 5a7 7 0 0 0 11.5-2',
}

function Icon({ name, size = 18 }: { name: IconName; size?: number }) {
  return (
    <svg aria-hidden="true" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
      <path d={iconPaths[name]} />
    </svg>
  )
}

function formatAmount(value: string | null | undefined) {
  if (!value) return '—'
  return value.startsWith('$') ? value : `$ ${value}`
}

function App() {
  const [metrics, setMetrics] = useState<Metric[]>([])
  const [metricsError, setMetricsError] = useState('')
  const [loadingMetrics, setLoadingMetrics] = useState(true)
  const [page, setPage] = useState<'overview' | 'reports' | 'assistant'>('overview')
  const [uploading, setUploading] = useState(false)
  const [uploadMessage, setUploadMessage] = useState('')
  const [isDragging, setIsDragging] = useState(false)
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: 'Hi there. I can help you explore the financials, risks, and growth drivers in your uploaded reports.' },
  ])
  const [question, setQuestion] = useState('')
  const [chatBusy, setChatBusy] = useState(false)
  const [chatError, setChatError] = useState('')
  const [health, setHealth] = useState<'checking' | 'online' | 'offline'>('checking')
  const fileInput = useRef<HTMLInputElement>(null)
  const chatEnd = useRef<HTMLDivElement>(null)

  async function loadMetrics() {
    setLoadingMetrics(true)
    setMetricsError('')
    try {
      const response = await fetch('/api/metrics')
      if (!response.ok) throw new Error(`Metrics request failed (${response.status})`)
      const data: Metric[] = await response.json()
      setMetricsError('')
      setMetrics(data)
    } catch (error) {
      setMetricsError(error instanceof Error ? error.message : 'Unable to load report metrics.')
    } finally {
      setLoadingMetrics(false)
    }
  }

  useEffect(() => {
    let cancelled = false

    async function initializeDashboard() {
      try {
        const response = await fetch('/api/metrics')
        if (!response.ok) throw new Error(`Metrics request failed (${response.status})`)
        const data: Metric[] = await response.json()
        if (!cancelled) setMetrics(data)
      } catch (error) {
        if (!cancelled) setMetricsError(error instanceof Error ? error.message : 'Unable to load report metrics.')
      } finally {
        if (!cancelled) setLoadingMetrics(false)
      }

      try {
        const response = await fetch('/health')
        if (!cancelled) setHealth(response.ok ? 'online' : 'offline')
      } catch {
        if (!cancelled) setHealth('offline')
      }
    }

    void initializeDashboard()
    return () => { cancelled = true }
  }, [])

  useEffect(() => {
    chatEnd.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, chatBusy])

  const companies = new Set(metrics.map((item) => item.company)).size
  const latestReport = [...metrics].sort((a, b) => b.created_at.localeCompare(a.created_at))[0]
  const revenueRows = metrics.filter((item) => item.revenue)
  const maxRevenue = Math.max(1, ...revenueRows.map((item) => Number(item.revenue?.replace(/[^\d.-]/g, '')) || 0))

  async function uploadFile(file?: File) {
    if (!file) return
    if (file.type !== 'application/pdf' && !file.name.toLowerCase().endsWith('.pdf')) {
      setUploadMessage('Please choose a PDF file.')
      return
    }

    setUploading(true)
    setUploadMessage('')
    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch('/api/upload', { method: 'POST', body: formData })
      const data = await response.json()
      if (!response.ok) throw new Error(data.detail ?? 'Upload failed. Please try again.')
      setUploadMessage(`${file.name} uploaded and analyzed successfully.`)
      await loadMetrics()
    } catch (error) {
      setUploadMessage(error instanceof Error ? error.message : 'Upload failed. Please try again.')
    } finally {
      setUploading(false)
      if (fileInput.current) fileInput.current.value = ''
    }
  }

  function onFileChange(event: ChangeEvent<HTMLInputElement>) {
    void uploadFile(event.target.files?.[0])
  }

  function onDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault()
    setIsDragging(false)
    void uploadFile(event.dataTransfer.files[0])
  }

  async function sendQuestion(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const text = question.trim()
    if (!text || chatBusy) return
    setMessages((current) => [...current, { role: 'user', content: text }])
    setQuestion('')
    setChatBusy(true)
    setChatError('')

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: text }),
      })
      const data = await response.json()
      if (!response.ok) throw new Error(data.detail ?? 'The assistant could not answer right now.')
      setMessages((current) => [...current, { role: 'assistant', content: data.answer }])
    } catch (error) {
      setChatError(error instanceof Error ? error.message : 'The assistant could not answer right now.')
    } finally {
      setChatBusy(false)
    }
  }

  const navItems: { key: typeof page; label: string; icon: IconName }[] = [
    { key: 'overview', label: 'Overview', icon: 'grid' },
    { key: 'reports', label: 'Reports', icon: 'file' },
    { key: 'assistant', label: 'AI assistant', icon: 'chat' },
  ]

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a className="brand" href="#" onClick={() => setPage('overview')}>
          <span className="brand-mark"><span /><span /><span /></span>
          <span className="brand-name">folio<span className="brand-period">.</span></span>
        </a>

        <div className="workspace-label">WORKSPACE</div>
        <nav className="main-nav" aria-label="Main navigation">
          {navItems.map((item) => (
            <button key={item.key} className={`nav-item ${page === item.key ? 'active' : ''}`} onClick={() => setPage(item.key)}>
              <Icon name={item.icon} size={19} />
              <span>{item.label}</span>
              {item.key === 'reports' && metrics.length > 0 && <span className="nav-count">{metrics.length}</span>}
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="upgrade-card">
            <div className="upgrade-icon"><Icon name="spark" size={17} /></div>
            <strong>Your reports, made clearer.</strong>
            <p>Ask questions and get grounded answers from your documents.</p>
            <button onClick={() => setPage('assistant')}>Try the assistant <Icon name="arrow" size={14} /></button>
          </div>
          <button className="profile-button">
            <span className="avatar">A</span>
            <span className="profile-copy"><strong>Analyst workspace</strong><small>Local environment</small></span>
            <span className={`health-dot ${health}`} title={`API ${health}`} />
          </button>
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <div className="breadcrumbs"><span>Workspace</span><span className="crumb-slash">/</span><strong>{page === 'overview' ? 'Overview' : page === 'reports' ? 'Reports' : 'AI assistant'}</strong></div>
          <div className="topbar-actions">
            <span className={`system-status ${health}`}><i />{health === 'online' ? 'All systems operational' : health === 'offline' ? 'API unavailable' : 'Checking services'}</span>
            <button className="icon-button" aria-label="Notifications"><Icon name="bell" /></button>
            <span className="top-avatar">A</span>
          </div>
        </header>

        <div className="page-content">
          {page === 'overview' && (
            <>
              <section className="welcome-row">
                <div>
                  <div className="eyebrow"><span className="eyebrow-dot" /> YOUR FINANCIAL INTELLIGENCE HUB</div>
                  <h1>Good morning<span className="heading-comma">,</span> Analyst</h1>
                  <p className="welcome-copy">A clearer view of your company reports starts here.</p>
                </div>
                <button className="primary-button" onClick={() => fileInput.current?.click()} disabled={uploading}>
                  <Icon name="plus" size={18} /> {uploading ? 'Analyzing report…' : 'Add a report'}
                </button>
                <input ref={fileInput} className="visually-hidden" type="file" accept="application/pdf,.pdf" onChange={onFileChange} />
              </section>

              {uploadMessage && (
                <div className={`notice ${uploadMessage.includes('successfully') ? 'success' : 'error'}`} role="status">
                  <Icon name={uploadMessage.includes('successfully') ? 'check' : 'close'} size={17} />
                  <span>{uploadMessage}</span>
                  <button aria-label="Dismiss message" onClick={() => setUploadMessage('')}><Icon name="close" size={15} /></button>
                </div>
              )}
              {metricsError && <div className="notice error" role="alert"><Icon name="close" size={17} /><span>{metricsError}</span><button onClick={() => void loadMetrics()}><Icon name="refresh" size={15} /> Retry</button></div>}

              <section className="stats-grid" aria-label="Report statistics">
                <article className="stat-card">
                  <div className="stat-card-top"><span className="stat-icon mint"><Icon name="file" /></span><span className="stat-caption">ALL TIME</span></div>
                  <div className="stat-value">{loadingMetrics ? '—' : metrics.length.toString().padStart(2, '0')}</div>
                  <div className="stat-label">Reports analyzed <span className="stat-trend"><Icon name="trend" size={14} /> Library</span></div>
                  <div className="stat-foot">Reports with extracted financials</div>
                </article>
                <article className="stat-card">
                  <div className="stat-card-top"><span className="stat-icon lilac"><Icon name="grid" /></span><span className="stat-caption">COVERAGE</span></div>
                  <div className="stat-value">{loadingMetrics ? '—' : companies.toString().padStart(2, '0')}</div>
                  <div className="stat-label">Companies tracked <span className="stat-neutral">Across your library</span></div>
                  <div className="stat-foot">Unique companies in your reports</div>
                </article>
                <article className="stat-card">
                  <div className="stat-card-top"><span className="stat-icon apricot"><Icon name="chart" /></span><span className="stat-caption">LATEST REPORT</span></div>
                  <div className="stat-value stat-value-amount">{loadingMetrics ? '—' : formatAmount(latestReport?.revenue)}</div>
                  <div className="stat-label">Latest reported revenue <span className="stat-neutral">{latestReport ? `${latestReport.company} · ${latestReport.year}` : 'No reports yet'}</span></div>
                  <div className="stat-foot">As stated in the source report</div>
                </article>
              </section>

              <section className="content-grid">
                <article className="panel revenue-panel">
                  <div className="panel-heading">
                    <div><h2>Revenue overview</h2><p>Reported revenue by company and year</p></div>
                    <button className="text-button" onClick={() => setPage('reports')}>View reports <Icon name="arrow" size={15} /></button>
                  </div>
                  {revenueRows.length === 0 ? (
                    <div className="chart-empty"><span className="empty-chart-icon"><Icon name="chart" size={22} /></span><strong>Your report insights will appear here</strong><p>Upload an annual report to see financial highlights.</p><button className="small-button" onClick={() => fileInput.current?.click()}><Icon name="plus" size={15} /> Add your first report</button></div>
                  ) : (
                    <div className="revenue-chart">
                      <div className="chart-axis"><span>100%</span><span>75%</span><span>50%</span><span>25%</span><span>0%</span></div>
                      <div className="chart-columns">
                        {revenueRows.slice(0, 6).map((item) => {
                          const amount = Number(item.revenue?.replace(/[^\d.-]/g, '')) || 0
                          return <div className="chart-column" key={`${item.company}-${item.year}`}><div className="bar-track"><div className="bar-value" style={{ height: `${Math.max(8, (amount / maxRevenue) * 100)}%` }} /></div><strong>{item.company}</strong><span>{item.year}</span></div>
                        })}
                      </div>
                    </div>
                  )}
                  {revenueRows.length > 0 && <div className="chart-legend"><span className="legend-dot" /> Revenue reported <span className="chart-unit">As presented in source documents</span></div>}
                </article>

                <article className="panel assistant-promo">
                  <div className="promo-orbit orbit-one" /><div className="promo-orbit orbit-two" />
                  <div className="promo-icon"><Icon name="spark" size={21} /></div>
                  <div className="promo-kicker">MEET YOUR RESEARCH ASSISTANT</div>
                  <h2>Better questions.<br />Clearer answers.</h2>
                  <p>Ask questions across your reports and get answers grounded in the source material.</p>
                  <button className="promo-button" onClick={() => setPage('assistant')}>Start a conversation <Icon name="arrow" size={16} /></button>
                  <div className="promo-foot"><Icon name="shield" size={15} /> Your documents stay in your local environment</div>
                </article>
              </section>

              <section className="panel reports-panel">
                <div className="panel-heading reports-heading">
                  <div><h2>Recent reports</h2><p>Your latest analyzed documents</p></div>
                  <button className="text-button" onClick={() => setPage('reports')}>See all <Icon name="arrow" size={15} /></button>
                </div>
                {metrics.length > 0 ? <ReportTable rows={metrics.slice(0, 5)} /> : (
                  <div className={`drop-zone ${isDragging ? 'dragging' : ''}`} onDragOver={(event) => { event.preventDefault(); setIsDragging(true) }} onDragLeave={() => setIsDragging(false)} onDrop={onDrop}>
                    <input ref={fileInput} className="visually-hidden" type="file" accept="application/pdf,.pdf" onChange={onFileChange} />
                    <span className="drop-icon"><Icon name="upload" size={21} /></span>
                    <div><strong>{uploading ? 'Analyzing your report…' : 'Drop a PDF here to get started'}</strong><p>PDF reports are processed locally and saved to your workspace.</p></div>
                    <button className="small-button" onClick={() => fileInput.current?.click()} disabled={uploading}>Browse files</button>
                  </div>
                )}
              </section>
              <footer className="page-footer"><span>Folio Intelligence</span><span><i className={`health-dot ${health}`} /> Local-first financial research</span></footer>
            </>
          )}

          {page === 'reports' && (
            <section className="reports-page">
              <div className="welcome-row">
                <div><div className="eyebrow"><span className="eyebrow-dot" /> YOUR DOCUMENT LIBRARY</div><h1>Reports</h1><p className="welcome-copy">Explore the financial metrics extracted from your reports.</p></div>
                <button className="primary-button" onClick={() => fileInput.current?.click()} disabled={uploading}><Icon name="plus" size={18} /> {uploading ? 'Analyzing…' : 'Add a report'}</button>
                <input ref={fileInput} className="visually-hidden" type="file" accept="application/pdf,.pdf" onChange={onFileChange} />
              </div>
              {metricsError && <div className="notice error" role="alert"><span>{metricsError}</span><button onClick={() => void loadMetrics()}>Retry</button></div>}
              <div className="library-summary"><span className="library-count">{metrics.length}</span><span>reports with financial data</span><button className="icon-button" aria-label="Refresh reports" onClick={() => void loadMetrics()}><Icon name="refresh" /></button></div>
              <div className="panel library-panel">{metrics.length ? <ReportTable rows={metrics} expanded /> : <div className="library-empty"><span className="empty-chart-icon"><Icon name="file" size={22} /></span><h2>No reports yet</h2><p>Upload a PDF report to extract financial data and make it searchable.</p><button className="primary-button" onClick={() => fileInput.current?.click()}><Icon name="upload" size={17} /> Upload a PDF</button></div>}</div>
            </section>
          )}

          {page === 'assistant' && (
            <section className="assistant-page">
              <div className="assistant-title"><div className="eyebrow"><span className="eyebrow-dot" /> DOCUMENT-GROUNDED RESEARCH</div><h1>Ask your reports<span className="heading-comma">.</span></h1><p className="welcome-copy">Get clear answers grounded in the documents in your workspace.</p></div>
              <div className="chat-card">
                <div className="chat-top"><div className="assistant-avatar"><Icon name="spark" size={19} /></div><div><strong>Folio assistant</strong><span><i className={`health-dot ${health}`} /> {health === 'online' ? 'Ready to help' : health === 'offline' ? 'API unavailable' : 'Connecting'}</span></div><button className="text-button chat-reset" onClick={() => { setMessages([{ role: 'assistant', content: 'Hi there. I can help you explore the financials, risks, and growth drivers in your uploaded reports.' }]); setChatError('') }}>New conversation <Icon name="plus" size={15} /></button></div>
                <div className="chat-messages">
                  {messages.map((message, index) => <div className={`message-row ${message.role}`} key={`${message.role}-${index}`}><div className={message.role === 'assistant' ? 'message-avatar' : 'user-message-avatar'}>{message.role === 'assistant' ? <Icon name="spark" size={15} /> : 'A'}</div><div className="message-bubble"><span className="message-author">{message.role === 'assistant' ? 'Folio assistant' : 'You'}</span><p>{message.content}</p></div></div>)}
                  {chatBusy && <div className="message-row assistant"><div className="message-avatar"><Icon name="spark" size={15} /></div><div className="message-bubble"><span className="message-author">Folio assistant</span><p className="typing-indicator"><i /><i /><i /> Searching your reports</p></div></div>}
                  <div ref={chatEnd} />
                </div>
                {chatError && <div className="chat-error" role="alert">{chatError}</div>}
                <form className="chat-compose" onSubmit={sendQuestion}><textarea value={question} onChange={(event) => setQuestion(event.target.value)} onKeyDown={(event) => { if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); event.currentTarget.form?.requestSubmit() } }} placeholder="Ask a question about your reports…" aria-label="Ask a question" rows={1} /><button className="send-button" type="submit" disabled={!question.trim() || chatBusy} aria-label="Send message"><Icon name="send" size={17} /></button></form>
                <div className="chat-disclaimer"><Icon name="shield" size={14} /> Responses are generated from your documents. Always verify important figures against the source.</div>
              </div>
              <div className="suggestion-row"><span>TRY ASKING</span>{['Summarize the latest report', 'What are the key financial risks?', 'Compare revenue across companies'].map((prompt) => <button key={prompt} onClick={() => setQuestion(prompt)}>{prompt} <Icon name="arrow" size={13} /></button>)}</div>
            </section>
          )}
        </div>
      </main>
    </div>
  )
}

function ReportTable({ rows, expanded = false }: { rows: Metric[]; expanded?: boolean }) {
  return (
    <div className="table-scroll">
      <table className="report-table">
        <thead><tr><th>COMPANY</th><th>FISCAL YEAR</th><th>REVENUE</th><th>NET INCOME</th><th>OPERATING INCOME</th><th>STATUS</th></tr></thead>
        <tbody>{rows.map((row) => <tr key={row.id}><td><span className="company-cell"><span className="company-monogram">{row.company.slice(0, 1).toUpperCase()}</span><strong>{row.company}</strong></span></td><td>{row.year}</td><td className="amount-cell">{formatAmount(row.revenue)}</td><td className="amount-cell">{formatAmount(row.net_income)}</td><td className="amount-cell">{formatAmount(row.operating_income)}</td><td><span className="status-pill"><i /> Analyzed</span></td></tr>)}</tbody>
      </table>
      {expanded && rows.length > 0 && <div className="table-note">Values are displayed as reported in each source document. Open a report in chat to explore further.</div>}
    </div>
  )
}

export default App
