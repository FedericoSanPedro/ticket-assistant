import pytest
from fastapi.testclient import TestClient

from app.llm import FakeClient
from app.main import app, get_llm


@pytest.fixture
def make_client():
    """Reemplaza el LLM real por FakeClient: rápido, gratis y determinístico."""

    def _make(llm=None):
        app.dependency_overrides[get_llm] = lambda: llm or FakeClient()
        return TestClient(app)

    yield _make
    app.dependency_overrides.clear()


def test_list_tickets(make_client):
    response = make_client().get("/api/tickets")

    assert response.status_code == 200
    tickets = response.json()
    assert len(tickets) == 4
    assert {"id", "customer", "title", "body"} <= tickets[0].keys()


def test_analyze_ticket_returns_structured_output(make_client):
    response = make_client().post("/api/tickets/1/analyze")

    assert response.status_code == 200
    assert response.json() == {
        "category": "billing",
        "priority": "high",
        "summary": "Resumen del ticket 1",
        "suggested_reply": "Hola, ya lo estamos revisando.",
    }


def test_analyze_unknown_ticket_returns_404(make_client):
    response = make_client().post("/api/tickets/999/analyze")

    assert response.status_code == 404


def test_analyze_llm_error_returns_422(make_client):
    response = make_client(FakeClient(fail=True)).post("/api/tickets/1/analyze")

    assert response.status_code == 422


def test_chat_streams_chunks(make_client):
    body = {"messages": [{"role": "user", "content": "hola"}]}

    with make_client().stream("POST", "/api/chat", json=body) as response:
        assert response.status_code == 200
        text = "".join(response.iter_text())

    assert text == "Hola, ¿en qué te ayudo?"


def test_chat_rejects_empty_messages(make_client):
    response = make_client().post("/api/chat", json={"messages": []})

    assert response.status_code == 422
