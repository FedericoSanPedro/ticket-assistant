import os
from collections.abc import AsyncIterator
from typing import Protocol

import anthropic
import ollama
from pydantic import ValidationError

from .schemas import ChatMessage, Ticket, TicketAnalysis

ANALYZE_SYSTEM = (
    "Sos un agente de soporte. Clasificá el ticket del cliente, asigná una prioridad "
    "y escribí una respuesta sugerida en español."
)
CHAT_SYSTEM = "Sos un asistente que ayuda al equipo de soporte. Respondé en español, de forma breve."


class LLMError(Exception):
    pass


class LLMClient(Protocol):
    """Interfaz que usan los endpoints. Cada proveedor la implementa a su manera."""

    async def analyze_ticket(self, ticket: Ticket) -> TicketAnalysis: ...

    def stream_chat(self, messages: list[ChatMessage]) -> AsyncIterator[str]: ...


def ticket_prompt(ticket: Ticket) -> str:
    return f"Cliente: {ticket.customer}\nTítulo: {ticket.title}\n\n{ticket.body}"


class OllamaClient:
    """Modelo local con Ollama: gratis y sin API key."""

    def __init__(self, client: ollama.AsyncClient | None = None) -> None:
        self._client = client or ollama.AsyncClient()
        self._model = os.getenv("OLLAMA_MODEL", "qwen2.5:0.5b")

    async def analyze_ticket(self, ticket: Ticket) -> TicketAnalysis:
        # format=<JSON schema> restringe la salida del modelo a ese schema.
        # Igual validamos con Pydantic: un modelo chico puede devolver valores raros.
        response = await self._client.chat(
            model=self._model,
            messages=[
                {"role": "system", "content": ANALYZE_SYSTEM},
                {"role": "user", "content": ticket_prompt(ticket)},
            ],
            format=TicketAnalysis.model_json_schema(),
        )
        try:
            return TicketAnalysis.model_validate_json(response.message.content)
        except ValidationError as e:
            raise LLMError("El modelo devolvió un análisis inválido") from e

    async def stream_chat(self, messages: list[ChatMessage]) -> AsyncIterator[str]:
        stream = await self._client.chat(
            model=self._model,
            messages=[{"role": "system", "content": CHAT_SYSTEM}, *(m.model_dump() for m in messages)],
            stream=True,
        )
        async for part in stream:
            yield part.message.content


class ClaudeClient:
    """Claude vía API de Anthropic (requiere ANTHROPIC_API_KEY, es pago)."""

    # Si el modelo rechaza una request por sus filtros de seguridad, la API la
    # reintenta sola con otro modelo. Es un beta, por eso va en extra_headers/extra_body.
    FALLBACK_OPTIONS = {
        "extra_headers": {"anthropic-beta": "server-side-fallback-2026-07-01"},
        "extra_body": {"fallbacks": "default"},
    }

    def __init__(self, client: anthropic.AsyncAnthropic | None = None) -> None:
        self._client = client or anthropic.AsyncAnthropic()
        self._model = os.getenv("ANTHROPIC_MODEL", "claude-opus-5-5")

    async def analyze_ticket(self, ticket: Ticket) -> TicketAnalysis:
        # messages.parse convierte el modelo Pydantic en un JSON schema, obliga al
        # LLM a respetarlo y devuelve la instancia ya validada en parsed_output.
        response = await self._client.messages.parse(
            model=self._model,
            max_tokens=16000,
            system=ANALYZE_SYSTEM,
            messages=[{"role": "user", "content": ticket_prompt(ticket)}],
            output_format=TicketAnalysis,
            **self.FALLBACK_OPTIONS,
        )
        if response.stop_reason == "refusal" or response.parsed_output is None:
            raise LLMError("El modelo no pudo analizar este ticket")
        return response.parsed_output

    async def stream_chat(self, messages: list[ChatMessage]) -> AsyncIterator[str]:
        async with self._client.messages.stream(
            model=self._model,
            max_tokens=64000,
            system=CHAT_SYSTEM,
            messages=[m.model_dump() for m in messages],
            **self.FALLBACK_OPTIONS,
        ) as stream:
            async for text in stream.text_stream:
                yield text


class FakeClient:
    """Respuestas fijas: para tests y para hacer la demo sin ningún modelo."""

    def __init__(self, fail: bool = False) -> None:
        self.fail = fail

    async def analyze_ticket(self, ticket: Ticket) -> TicketAnalysis:
        if self.fail:
            raise LLMError("El modelo no pudo analizar este ticket")
        return TicketAnalysis(
            category="billing",
            priority="high",
            summary=f"Resumen del ticket {ticket.id}",
            suggested_reply="Hola, ya lo estamos revisando.",
        )

    async def stream_chat(self, messages: list[ChatMessage]) -> AsyncIterator[str]:
        for chunk in ["Hola", ", ", "¿en qué te ayudo?"]:
            yield chunk


def create_llm_client() -> LLMClient:
    provider = os.getenv("LLM_PROVIDER", "ollama")
    if provider == "ollama":
        return OllamaClient()
    if provider == "claude":
        return ClaudeClient()
    if provider == "fake":
        return FakeClient()
    raise ValueError(f"LLM_PROVIDER desconocido: {provider}")
