import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { fireEvent, render, screen } from '@testing-library/react'
import type { ReactElement } from 'react'
import { describe, expect, it, vi } from 'vitest'
import { TicketList } from './TicketList'

const tickets = [{ id: 1, customer: 'Lucía', title: 'Me cobraron dos veces', body: 'Dos cargos.' }]
const analysis = {
  category: 'billing',
  priority: 'high',
  summary: 'Cobro duplicado',
  suggested_reply: 'Te devolvemos el cargo.',
}

function renderWithQueryClient(ui: ReactElement) {
  // retry: false para que un error falle al toque en vez de reintentar.
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(<QueryClientProvider client={client}>{ui}</QueryClientProvider>)
}

describe('TicketList', () => {
  it('muestra los tickets que devuelve la API', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(Response.json(tickets)))

    renderWithQueryClient(<TicketList />)

    expect(screen.getByText('Cargando tickets...')).toBeInTheDocument()
    expect(await screen.findByText('Me cobraron dos veces')).toBeInTheDocument()
  })

  it('muestra el análisis al apretar el botón', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn((url: string) => Promise.resolve(Response.json(url.endsWith('/analyze') ? analysis : tickets))),
    )

    renderWithQueryClient(<TicketList />)
    fireEvent.click(await screen.findByRole('button', { name: 'Analizar con IA' }))

    expect(await screen.findByText('Cobro duplicado')).toBeInTheDocument()
    expect(screen.getByText('high')).toBeInTheDocument()
  })

  it('muestra un error si la API falla', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(null, { status: 500 })))

    renderWithQueryClient(<TicketList />)

    expect(await screen.findByRole('alert')).toHaveTextContent('No se pudieron cargar')
  })
})
