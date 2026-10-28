import { describe, expect, it, vi } from 'vitest'
import { streamChat } from './api'

function streamingResponse(chunks: string[]): Response {
  const encoder = new TextEncoder()
  const body = new ReadableStream<Uint8Array>({
    start(controller) {
      chunks.forEach((c) => controller.enqueue(encoder.encode(c)))
      controller.close()
    },
  })
  return new Response(body, { status: 200 })
}

describe('streamChat', () => {
  it('llama a onChunk con cada pedazo de la respuesta', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(streamingResponse(['Hola', ', ', 'mundo'])))
    const chunks: string[] = []

    await streamChat([{ role: 'user', content: 'hola' }], (c) => chunks.push(c))

    expect(chunks.join('')).toBe('Hola, mundo')
    expect(fetch).toHaveBeenCalledWith('/api/chat', expect.objectContaining({ method: 'POST' }))
  })

  it('tira error si el backend responde con error', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(null, { status: 500 })))

    await expect(streamChat([{ role: 'user', content: 'hola' }], () => {})).rejects.toThrow('500')
  })
})
