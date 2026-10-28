import asyncio
from types import SimpleNamespace

import pytest

from app.llm import LLMError, OllamaClient
from app.schemas import Ticket

TICKET = Ticket(id=1, customer="Lucía", title="Cobro doble", body="Me cobraron dos veces.")


class StubOllama:
    """Imita ollama.AsyncClient devolviendo un contenido fijo."""

    def __init__(self, content: str) -> None:
        self.content = content

    async def chat(self, **kwargs):
        return SimpleNamespace(message=SimpleNamespace(content=self.content))


def test_parses_valid_json():
    content = '{"category": "billing", "priority": "high", "summary": "Cobro doble", "suggested_reply": "Lo revisamos."}'

    analysis = asyncio.run(OllamaClient(StubOllama(content)).analyze_ticket(TICKET))

    assert analysis.category == "billing"
    assert analysis.priority == "high"


def test_invalid_output_raises_llm_error():
    # Un modelo chico podría inventar una categoría que no existe.
    content = '{"category": "pizza", "priority": "high", "summary": "x", "suggested_reply": "y"}'

    with pytest.raises(LLMError):
        asyncio.run(OllamaClient(StubOllama(content)).analyze_ticket(TICKET))
