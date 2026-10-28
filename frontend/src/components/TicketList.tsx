import { useMutation, useQuery } from '@tanstack/react-query'
import { analyzeTicket, fetchTickets, type Ticket } from '../api'

export function TicketList() {
  // useQuery se encarga del cache, loading, error y reintentos.
  const { data: tickets, isPending, isError } = useQuery({
    queryKey: ['tickets'],
    queryFn: fetchTickets,
  })

  if (isPending) return <p>Cargando tickets...</p>
  if (isError) return <p role="alert">No se pudieron cargar los tickets.</p>

  return (
    <ul className="ticket-list">
      {tickets.map((ticket) => (
        <TicketCard key={ticket.id} ticket={ticket} />
      ))}
    </ul>
  )
}

function TicketCard({ ticket }: { ticket: Ticket }) {
  // useMutation para acciones que el usuario dispara (POST), no para leer datos.
  const analysis = useMutation({ mutationFn: () => analyzeTicket(ticket.id) })

  return (
    <li className="card">
      <h3>{ticket.title}</h3>
      <p className="muted">{ticket.customer}</p>
      <p>{ticket.body}</p>

      <button onClick={() => analysis.mutate()} disabled={analysis.isPending}>
        {analysis.isPending ? 'Analizando...' : 'Analizar con IA'}
      </button>

      {analysis.isError && <p role="alert">Falló el análisis.</p>}
      {analysis.data && (
        <div className="analysis">
          <span className="tag">{analysis.data.category}</span>
          <span className={`tag priority-${analysis.data.priority}`}>{analysis.data.priority}</span>
          <p>{analysis.data.summary}</p>
          <p className="muted">Respuesta sugerida: {analysis.data.suggested_reply}</p>
        </div>
      )}
    </li>
  )
}
