import { useState, type FormEvent } from 'react'
import { streamChat, type ChatMessage } from '../api'

export function Chat() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    const text = input.trim()
    if (!text || isStreaming) return

    const history: ChatMessage[] = [...messages, { role: 'user', content: text }]
    // Agregamos un mensaje vacío del asistente que se va llenando con cada chunk.
    setMessages([...history, { role: 'assistant', content: '' }])
    setInput('')
    setError(null)
    setIsStreaming(true)

    try {
      await streamChat(history, (chunk) => {
        setMessages((prev) => {
          const last = prev[prev.length - 1]
          return [...prev.slice(0, -1), { ...last, content: last.content + chunk }]
        })
      })
    } catch {
      setError('Hubo un error al obtener la respuesta.')
    } finally {
      setIsStreaming(false)
    }
  }

  return (
    <section className="chat">
      <div className="messages">
        {messages.map((m, i) => (
          <p key={i} className={`message ${m.role}`}>
            {m.content}
          </p>
        ))}
        {error && <p role="alert">{error}</p>}
      </div>
      <form onSubmit={handleSubmit}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Preguntá algo..."
          aria-label="Mensaje"
        />
        <button type="submit" disabled={isStreaming}>
          Enviar
        </button>
      </form>
    </section>
  )
}
