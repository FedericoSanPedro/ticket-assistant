// Tipos que reflejan los modelos Pydantic del backend (app/schemas.py).
export type Ticket = {
  id: number
  customer: string
  title: string
  body: string
}

export type TicketAnalysis = {
  category: 'billing' | 'bug' | 'feature_request' | 'account' | 'other'
  priority: 'low' | 'medium' | 'high'
  summary: string
  suggested_reply: string
}

export type ChatMessage = {
  role: 'user' | 'assistant'
  content: string
}

async function getJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    throw new Error(`Error ${response.status}`)
  }
  return response.json() as Promise<T>
}

export async function fetchTickets(): Promise<Ticket[]> {
  return getJson(await fetch('/api/tickets'))
}

export async function analyzeTicket(id: number): Promise<TicketAnalysis> {
  return getJson(await fetch(`/api/tickets/${id}/analyze`, { method: 'POST' }))
}

/**
 * Llama a /api/chat y va pasando cada pedazo de texto a onChunk a medida que llega,
 * en vez de esperar a que termine toda la respuesta.
 */
export async function streamChat(
  messages: ChatMessage[],
  onChunk: (text: string) => void,
): Promise<void> {
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ messages }),
  })
  if (!response.ok || !response.body) {
    throw new Error(`Error ${response.status}`)
  }

  const reader = response.body.getReader()
  // stream: true evita romper caracteres (tildes, ñ) que lleguen partidos entre dos chunks.
  const decoder = new TextDecoder()
  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    onChunk(decoder.decode(value, { stream: true }))
  }
}
