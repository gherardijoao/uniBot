import React, { useState } from 'react'
import { motion } from 'framer-motion'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import './styles.css'

export default function App() {
  const [query, setQuery] = useState('')
  const [resp, setResp] = useState(null)
  const [loading, setLoading] = useState(false)

  async function send() {
    try {
      setLoading(true)
      console.log('Enviando query para /api/query')
      
      const r = await fetch('/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      })

      if (!r.ok) {
        const errorText = await r.text();
        throw new Error(`Erro ${r.status}: ${errorText || r.statusText}`);
      }

      const j = await r.json()
      setResp(j)
    } catch (e) {
      setResp({ response: 'Erro ao chamar a API: ' + String(e), docs_found: 0 })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app-shell">
      <motion.main
        className="center-stage"
        initial={{ opacity: 0, scale: 0.98 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5, ease: 'easeOut' }}
      >
        <motion.section
          className="chat-card"
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45, delay: 0.05, ease: 'easeOut' }}
        >
          <div className="minimal-header">
            <span className="eyebrow">uniBot</span>
            <h1>Pergunte e receba a resposta</h1>
            <p>
              Uma interface limpa, escura e centralizada para consultar documentos da universidade.
            </p>
          </div>

          <label className="field-label" htmlFor="query">
            Sua pergunta
          </label>

          <div className="input-stack">
            <textarea
              id="query"
              value={query}
              onChange={e => setQuery(e.target.value)}
              placeholder="Ex.: Qual é o objetivo da Resolução CEPE 473?"
              rows={5}
            />
            <button className="primary-button" onClick={send} disabled={loading} type="button">
              {loading ? 'Gerando...' : 'Enviar'}
            </button>
          </div>

          <div className="response-area">
            <div className="response-label">Resposta</div>

            {!resp && <div className="empty-state">Ainda não há resposta. Faça uma pergunta para começar.</div>}

            {resp && (
              <motion.div
                className="response-card"
                initial={{ opacity: 0, scale: 0.98 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.25 }}
              >
                <div className="markdown-content">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {resp.response}
                  </ReactMarkdown>
                </div>
                <div className="response-meta">
                  <span>{resp.docs_found} documento(s) consultado(s)</span>
                </div>
              </motion.div>
            )}
          </div>
        </motion.section>
      </motion.main>
    </div>
  )
}
