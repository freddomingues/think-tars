import { useState, useEffect, useRef } from 'react'

const API = '/api/demos' // backend mantém prefixo /api/demos; UI exibe "Playground"

export default function App() {
  const [assistants, setAssistants] = useState([])
  const [selected, setSelected] = useState(null)
  const [conversationId, setConversationId] = useState(null)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [pdfFile, setPdfFile] = useState(null)
  const [uploadProgress, setUploadProgress] = useState(null)
  const bottomRef = useRef(null)
  const fileInputRef = useRef(null)

  useEffect(() => {
    fetch(`${API}/assistants`)
      .then((r) => r.json())
      .then((d) => {
        setAssistants(d.assistants || [])
        if (d.assistants?.length && !selected) setSelected(d.assistants[0].id)
      })
      .catch(() => setError('Não foi possível carregar assistentes.'))
  }, [])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleFileSelect = (e) => {
    const file = e.target.files?.[0]
    if (file) {
      if (!file.name.toLowerCase().endsWith('.pdf')) {
        setError('Apenas arquivos PDF são suportados.')
        return
      }
      setPdfFile(file)
      setError(null)
    }
  }

  const startConversation = async () => {
    if (!selected) return
    setLoading(true)
    setError(null)
    setUploadProgress(null)
    if (conversationId) setMessages([])

    try {
      let conversationData

      if (pdfFile) {
        setUploadProgress('Processando PDF...')
        const formData = new FormData()
        formData.append('file', pdfFile)
        formData.append('agent_id', selected)

        const uploadRes = await fetch(`${API}/upload-pdf`, {
          method: 'POST',
          body: formData,
        })

        const uploadData = await uploadRes.json()
        if (!uploadRes.ok) throw new Error(uploadData.error || 'Erro ao processar PDF')

        conversationData = uploadData
        setUploadProgress('PDF processado com sucesso!')
        setTimeout(() => setUploadProgress(null), 2000)
      } else {
        const r = await fetch(`${API}/conversations`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ agent_id: selected }),
        })
        conversationData = await r.json()
        if (!r.ok) throw new Error(conversationData.error || 'Erro ao criar conversa')
      }

      setConversationId(conversationData.conversation_id)
      setMessages([])
      setPdfFile(null)
      if (fileInputRef.current) fileInputRef.current.value = ''
    } catch (e) {
      setError(e.message)
      setUploadProgress(null)
    } finally {
      setLoading(false)
    }
  }

  const sendMessage = async () => {
    const text = input.trim()
    if (!text || !conversationId || loading) return
    setInput('')
    setMessages((m) => [...m, { role: 'user', content: text }])
    setLoading(true)
    setError(null)
    try {
      const r = await fetch(`${API}/conversations/${conversationId}/messages`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: text }),
      })
      const d = await r.json()
      if (!r.ok) throw new Error(d.error || 'Erro ao enviar mensagem')
      if (d.error) {
        setMessages((m) => [...m, { role: 'assistant', content: d.error, isError: true }])
      } else {
        setMessages((m) => [...m, { role: 'assistant', content: d.message }])
      }
    } catch (e) {
      setError(e.message)
      setMessages((m) => [...m, { role: 'assistant', content: e.message, isError: true }])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const currentName = assistants.find((a) => a.id === selected)?.name || 'Assistente'

  const scrollTo = (id) => {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' })
  }

  return (
    <>
      {/* Nav — mesmo estilo Think TARS: Início, Sobre, Projetos, Contato */}
      <nav className="nav" aria-label="Navegação principal">
        <a href="#inicio" className="nav-logo" onClick={(e) => { e.preventDefault(); scrollTo('inicio') }}>
          Think <span>TARS</span>
        </a>
        <ul className="nav-links">
          <li><a href="#inicio" onClick={(e) => { e.preventDefault(); scrollTo('inicio') }}>Início</a></li>
          <li><a href="#sobre" onClick={(e) => { e.preventDefault(); scrollTo('sobre') }}>Sobre</a></li>
          <li><a href="#projetos" onClick={(e) => { e.preventDefault(); scrollTo('projetos') }}>Projetos</a></li>
          <li><a href="#contato" onClick={(e) => { e.preventDefault(); scrollTo('contato') }}>Contato</a></li>
        </ul>
      </nav>

      {/* Seção Início — Hero */}
      <section id="inicio" className="hero">
        <span className="hero-badge">Tecnologia que entrega eficiência</span>
        <h1>Soluções que liberam o seu tempo</h1>
        <p>
          Conheça a Think TARS. Automação para problemas reais — criamos tecnologia que funciona de verdade para você ganhar tempo e focar no que importa.
        </p>
        <a href="#projetos" className="hero-cta" onClick={(e) => { e.preventDefault(); scrollTo('projetos') }}>
          Confira os Projetos
        </a>
      </section>

      {/* Seção Sobre */}
      <section id="sobre" className="section">
        <h2 className="section-title">Automação para problemas reais</h2>
        <p className="section-subtitle">Acreditamos que só existe um recurso que é possível de escalar: o seu tempo!</p>
        <div className="quote-block">
          <span className="led" aria-hidden="true" />
          <p><strong>Criamos tecnologia que funciona de verdade.</strong> Para você ganhar tempo e focar no que importa!</p>
        </div>
      </section>

      {/* Seção Projetos — Cards + Playground */}
      <section id="projetos" className="section">
        <h2 className="section-title">Soluções Eficientes</h2>
        <p className="section-subtitle">Porque acreditamos que automatizar é a única forma de não afundar no tempo</p>

        <div className="cards-grid">
          <div className="card">
            <h3>Assistente Jurídico</h3>
            <p>Agente de IA para responder detalhes específicos de contratos dos clientes, com busca em base de conhecimento.</p>
            <a href="#playground-chat" onClick={(e) => { e.preventDefault(); scrollTo('playground-chat') }}>Saiba mais</a>
          </div>
          <div className="card">
            <h3>Agente de Investimento</h3>
            <p>Análise de mercado e sugestões de trading (Bitcoin) com estratégia conservadora e ferramentas de execução.</p>
            <a href="#playground-chat" onClick={(e) => { e.preventDefault(); scrollTo('playground-chat') }}>Saiba mais</a>
          </div>
          <div className="card">
            <h3>Analista de Planilha</h3>
            <p>Consulta e análise de dados em planilhas Excel via linguagem natural.</p>
            <a href="#playground-chat" onClick={(e) => { e.preventDefault(); scrollTo('playground-chat') }}>Saiba mais</a>
          </div>
          <div className="card">
            <h3>Playground</h3>
            <p>Converse com os assistentes de IA. Envie um PDF opcional como base de conhecimento e realize seus testes em tempo real.</p>
            <a href="#playground-chat" onClick={(e) => { e.preventDefault(); scrollTo('playground-chat') }}>Abrir Playground</a>
          </div>
        </div>

        {/* Área do chat (Playground) */}
        <div id="playground-chat" className="demos-wrapper">
          <div className="demos-header">Playground — Assistentes de IA</div>
          <div style={{ display: 'flex', flex: 1, minHeight: 420 }}>
            <aside className="chat-sidebar">
              <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>Assistente</label>
              <select
                value={selected || ''}
                onChange={(e) => {
                  setSelected(e.target.value)
                  setConversationId(null)
                  setMessages([])
                  setPdfFile(null)
                  if (fileInputRef.current) fileInputRef.current.value = ''
                }}
                style={{
                  padding: '0.5rem 0.75rem',
                  background: 'var(--bg)',
                  border: '1px solid var(--border)',
                  borderRadius: 6,
                  color: 'var(--text)',
                  fontFamily: 'var(--font-sans)',
                  fontSize: '0.9rem',
                }}
                disabled={!!conversationId}
              >
                {assistants.map((a) => (
                  <option key={a.id} value={a.id}>{a.name}</option>
                ))}
              </select>

              {!conversationId && (
                <>
                  <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>Base de Conhecimento (opcional)</label>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".pdf"
                    onChange={handleFileSelect}
                    style={{
                      padding: '0.5rem',
                      background: 'var(--bg)',
                      border: '1px solid var(--border)',
                      borderRadius: 6,
                      color: 'var(--text)',
                      fontFamily: 'var(--font-sans)',
                      fontSize: '0.85rem',
                      cursor: 'pointer',
                    }}
                    disabled={loading}
                  />
                  {pdfFile && (
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.5rem 0.75rem', background: 'var(--accent-dim)', border: '1px solid var(--accent)', borderRadius: 6 }}>
                      <span style={{ fontSize: '0.85rem', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{pdfFile.name}</span>
                      <button
                        type="button"
                        onClick={() => { setPdfFile(null); if (fileInputRef.current) fileInputRef.current.value = '' }}
                        style={{ background: 'none', border: 'none', color: 'var(--text-muted)', fontSize: '1.5rem', cursor: 'pointer', padding: '0 0.25rem' }}
                      >
                        ×
                      </button>
                    </div>
                  )}
                  {uploadProgress && <div style={{ fontSize: '0.85rem', color: 'var(--accent)', textAlign: 'center', padding: '0.5rem' }}>{uploadProgress}</div>}
                </>
              )}

              <button
                type="button"
                onClick={startConversation}
                disabled={loading || !selected}
                style={{
                  padding: '0.5rem 1rem',
                  background: 'var(--accent)',
                  border: 'none',
                  borderRadius: 6,
                  color: 'var(--bg)',
                  fontFamily: 'var(--font-sans)',
                  fontWeight: 500,
                  cursor: loading || !selected ? 'not-allowed' : 'pointer',
                  marginTop: '0.5rem',
                }}
              >
                {conversationId ? 'Nova conversa' : pdfFile ? 'Processar PDF e Iniciar' : 'Iniciar conversa'}
              </button>
              {conversationId && (
                <button
                  type="button"
                  onClick={() => { setConversationId(null); setMessages([]); setPdfFile(null); if (fileInputRef.current) fileInputRef.current.value = '' }}
                  style={{
                    padding: '0.4rem 0.75rem',
                    background: 'transparent',
                    border: '1px solid var(--border)',
                    borderRadius: 6,
                    color: 'var(--text-muted)',
                    fontFamily: 'var(--font-sans)',
                    fontSize: '0.85rem',
                    cursor: 'pointer',
                  }}
                >
                  Trocar assistente
                </button>
              )}
            </aside>

            <div className="chat-main chat-layout">
              {!conversationId ? (
                <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', color: 'var(--text-muted)', padding: '2rem', textAlign: 'center' }}>
                  <p>Selecione um assistente e opcionalmente faça upload de um PDF.</p>
                  <p style={{ fontSize: '0.9rem' }}>Assistente atual: {currentName}</p>
                  <p style={{ fontSize: '0.85rem', fontStyle: 'italic', maxWidth: 400 }}>Faça upload de um PDF para que o assistente se torne especialista no conteúdo do documento.</p>
                </div>
              ) : (
                <>
                  <div className="chat-messages">
                    {messages.map((msg, i) => (
                      <div
                        key={i}
                        style={{
                          maxWidth: '85%',
                          padding: '0.75rem 1rem',
                          borderRadius: 12,
                          alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                          background: msg.role === 'user' ? 'var(--accent-dim)' : 'var(--surface)',
                          border: `1px solid ${msg.role === 'user' ? 'var(--accent)' : 'var(--border)'}`,
                          ...(msg.isError && { borderColor: 'var(--error)', color: 'var(--error)' }),
                        }}
                      >
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.25rem' }}>
                          {msg.role === 'user' ? 'Você' : currentName}
                        </span>
                        <div style={{ fontSize: '0.95rem', whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>{msg.content}</div>
                      </div>
                    ))}
                    {loading && (
                      <div style={{ maxWidth: '85%', padding: '0.75rem 1rem', borderRadius: 12, alignSelf: 'flex-start', background: 'var(--surface)', border: '1px solid var(--border)' }}>
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{currentName}</span>
                        <div style={{ fontSize: '0.95rem' }}>...</div>
                      </div>
                    )}
                    <div ref={bottomRef} />
                  </div>
                  <div className="chat-input-row">
                    <textarea
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      onKeyDown={handleKeyDown}
                      placeholder="Digite sua mensagem..."
                      rows={2}
                      style={{
                        flex: 1,
                        padding: '0.6rem 0.75rem',
                        background: 'var(--bg)',
                        border: '1px solid var(--border)',
                        borderRadius: 8,
                        color: 'var(--text)',
                        fontFamily: 'var(--font-sans)',
                        fontSize: '0.95rem',
                        resize: 'none',
                      }}
                      disabled={loading}
                    />
                    <button
                      type="button"
                      onClick={sendMessage}
                      disabled={loading || !input.trim()}
                      style={{
                        padding: '0.6rem 1.25rem',
                        background: 'var(--accent)',
                        border: 'none',
                        borderRadius: 8,
                        color: 'var(--bg)',
                        fontFamily: 'var(--font-sans)',
                        fontWeight: 500,
                        cursor: loading || !input.trim() ? 'not-allowed' : 'pointer',
                      }}
                    >
                      Enviar
                    </button>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* Seção Contato */}
      <section id="contato" className="contact-section">
        <h2 className="section-title">Entre em Contato</h2>
        <p>Tem alguma ideia para o seu negócio? Quer saber mais sobre nossas soluções em IA?</p>
        <a href="https://wa.me/554187497364" target="_blank" rel="noopener noreferrer">Nos conte sua ideia e tire todas as suas dúvidas, fale agora mesmo com um dos nossos especialistas especialista</a>
      </section>

      {/* Footer — Think TARS style */}
      <footer className="footer">
        <p className="footer-brand">Think <span>TARS</span></p>
        <p className="footer-tagline">Think AI for Real Solutions</p>
        <p className="footer-copy">© {new Date().getFullYear()}. All rights reserved.</p>
      </footer>

      {error && (
        <div
          role="alert"
          style={{
            position: 'fixed',
            bottom: '1rem',
            left: '50%',
            transform: 'translateX(-50%)',
            padding: '0.75rem 1rem',
            background: 'var(--surface)',
            border: '1px solid var(--error)',
            borderRadius: 8,
            color: 'var(--error)',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            zIndex: 9999,
          }}
        >
          {error}
          <button
            type="button"
            onClick={() => setError(null)}
            style={{ background: 'none', border: 'none', color: 'inherit', fontSize: '1.25rem', cursor: 'pointer', padding: '0 0.25rem' }}
          >
            ×
          </button>
        </div>
      )}
    </>
  )
}
