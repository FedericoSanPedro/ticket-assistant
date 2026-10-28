from typing import Literal

from pydantic import BaseModel, Field


class Ticket(BaseModel):
    id: int
    customer: str
    title: str
    body: str


class TicketAnalysis(BaseModel):
    """Salida estructurada que le pedimos al LLM. Pydantic genera el JSON schema
    y valida la respuesta, así el frontend recibe siempre la misma forma."""

    category: Literal["billing", "bug", "feature_request", "account", "other"]
    priority: Literal["low", "medium", "high"]
    summary: str = Field(description="Resumen del problema en una oración")
    suggested_reply: str = Field(description="Respuesta breve y amable para el cliente")


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1)


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1)
