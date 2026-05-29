import React, { useState } from 'react'

export default function App() {
  const [query, setQuery] = useState('')
  const [resp, setResp] = useState(null)

  async function send() {
    const r = await fetch('/api/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query })
    })
    const j = await r.json()
    setResp(j)
  }

  return (
    <div style={{ padding: 20 }}>
      <h1>uniBot (protótipo)</h1>
      <input value={query} onChange={e => setQuery(e.target.value)} placeholder="Pergunte algo" style={{ width: '60%' }} />
      <button onClick={send} style={{ marginLeft: 8 }}>Enviar</button>
      <pre style={{ marginTop: 20 }}>{resp ? JSON.stringify(resp, null, 2) : 'Sem resposta'}</pre>
    </div>
  )
}
