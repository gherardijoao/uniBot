import React, { useState } from 'react'

export default function App() {
  const [query, setQuery] = useState('')
  const [resp, setResp] = useState(null)
  const [loading, setLoading] = useState(false)

  async function send() {
    try {
      setLoading(true)
      const r = await fetch('/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      })
      const j = await r.json()
      setResp(j)
    } catch (e) {
      setResp({ response: 'Erro ao chamar a API: ' + String(e), docs_found: 0 })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ padding: 20 }}>
      <h1>uniBot (protótipo)</h1>
      <input value={query} onChange={e => setQuery(e.target.value)} placeholder="Pergunte algo" style={{ width: '60%' }} />
      <button onClick={send} style={{ marginLeft: 8 }} disabled={loading}>{loading ? 'Enviando...' : 'Enviar'}</button>
      <div style={{ marginTop: 20 }}>
        {!resp && <div>Sem resposta</div>}
        {resp && (
          <div>
            <h3>Resposta</h3>
            <div style={{ whiteSpace: 'pre-wrap', background: '#f6f8fa', padding: 12, borderRadius: 6 }}>{resp.response}</div>
            <p style={{ marginTop: 8 }}><strong>Documentos encontrados:</strong> {resp.docs_found}</p>
          </div>
        )}
      </div>
    </div>
  )
}
