import { Chat } from './components/Chat'
import { TicketList } from './components/TicketList'
import './App.css'

export default function App() {
  return (
    <main className="layout">
      <section>
        <h2>Tickets</h2>
        <TicketList />
      </section>
      <section>
        <h2>Asistente</h2>
        <Chat />
      </section>
    </main>
  )
}
