from .schemas import Ticket

# En un proyecto real esto vendría de una base de datos.
TICKETS: list[Ticket] = [
    Ticket(
        id=1,
        customer="Lucía Fernández",
        title="Me cobraron dos veces",
        body="Este mes veo dos cargos iguales en mi tarjeta por la suscripción Pro. Necesito que me devuelvan uno.",
    ),
    Ticket(
        id=2,
        customer="Martín Gómez",
        title="La app se cierra al exportar",
        body="Cada vez que intento exportar un reporte a PDF la aplicación se cierra sola. Uso Windows 11.",
    ),
    Ticket(
        id=3,
        customer="Sofía Ruiz",
        title="¿Se puede integrar con Slack?",
        body="Sería genial recibir las alertas en un canal de Slack en lugar de por mail.",
    ),
    Ticket(
        id=4,
        customer="Diego Morales",
        title="No puedo entrar a mi cuenta",
        body="Restablecí la contraseña dos veces y sigue diciendo que es incorrecta. Tengo una demo con un cliente en una hora.",
    ),
]


def get_ticket(ticket_id: int) -> Ticket | None:
    return next((t for t in TICKETS if t.id == ticket_id), None)
