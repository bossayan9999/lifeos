import React, { useState, useRef, useEffect } from 'react'
import axios from 'axios'
import './ChatInterface.css'

export default function ChatInterface({ activePlugin }) {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'LifeOS ready. Ask anything about your knowledge base. Local retrieval runs first; external systems only when needed.',
      citations: [],
      meta: null,
    },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const send = async () => {
    const q = input.trim()
    if (!q || loading) return

    setMessages(m => [...m, { role: 'user', content: q }])
    setInput('')
    setLoading(true)

    try {
      const { data } = await axios.post('/api/v1/query', {
        query: q,
        top_k: 5,
        use_web: false,
        plugin: activePlugin || undefined,
      })

      setMessages(m => [
        ...m,
        {
          role: 'assistant',
          content: data.answer,
          citations: data.citations || [],
          meta: {
            confidence: data.confidence,
            used_web: data.used_web,
            used_plugin: data.used_plugin,
            ms: data.processing_ms,
          },
        },
      ])
    } catch (err) {
      setMessages(m => [
        ...m,
        {
          role: 'assistant',
          content: 'Backend unreachable. Start the FastAPI server on port 8000.',
          citations: [],
          meta: null,
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  const onKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      send()
    }
  }

  return (
    <div className="chat">
      <div className="messages">
        {messages.map((msg, i) => (
          <div key={i} className={`msg msg-${msg.role}`}>
            <div className="msg-bubble">
              <div className="msg-content">{msg.content}</div>

              {msg.citations?.length > 0 && (
                <div className="citations">
                  <div className="citations-title">Sources</div>
                  {msg.citations.map((c, j) => (
                    <div key={j} className="citation">
                      <span className="citation-score">{(c.score * 100).toFixed(0)}%</span>
                      <span className="citation-title">{c.title}</span>
                      <span className="citation-type">{c.source_type}</span>
                    </div>
                  ))}
                </div>
              )}

              {msg.meta && (
                <div className="meta">
                  conf {msg.meta.confidence?.toFixed(2)}
                  {msg.meta.used_web && ' · web'}
                  {msg.meta.used_plugin && ` · ${msg.meta.used_plugin}`}
                  {msg.meta.ms != null && ` · ${msg.meta.ms}ms`}
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="msg msg-assistant">
            <div className="msg-bubble loading">Thinking…</div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="composer">
        {activePlugin && (
          <div className="active-plugin-chip">
            Plugin: <strong>{activePlugin}</strong>
          </div>
        )}
        <div className="composer-row">
          <textarea
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={onKey}
            placeholder={activePlugin ? `Ask via ${activePlugin} plugin…` : 'Ask your knowledge base…'}
            rows={1}
          />
          <button className="send-btn" onClick={send} disabled={loading || !input.trim()}>
            Send
          </button>
        </div>
      </div>
    </div>
  )
}
