from functools import lru_cache
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import StreamingResponse

from .data import TICKETS, get_ticket
from .llm import LLMClient, LLMError, create_llm_client
from .schemas import ChatRequest, Ticket, TicketAnalysis

app = FastAPI(title="Ticket Assistant")


@lru_cache
def get_llm() -> LLMClient:
    return create_llm_client()


LLM = Annotated[LLMClient, Depends(get_llm)]


@app.get("/api/tickets", response_model=list[Ticket])
def list_tickets() -> list[Ticket]:
    return TICKETS


@app.post("/api/tickets/{ticket_id}/analyze", response_model=TicketAnalysis)
async def analyze_ticket(ticket_id: int, llm: LLM) -> TicketAnalysis:
    ticket = get_ticket(ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    try:
        return await llm.analyze_ticket(ticket)
    except LLMError as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.post("/api/chat")
async def chat(request: ChatRequest, llm: LLM) -> StreamingResponse:
    # Mandamos texto plano en chunks: el frontend lo lee con un ReadableStream.
    return StreamingResponse(
        llm.stream_chat(request.messages),
        media_type="text/plain; charset=utf-8",
    )
