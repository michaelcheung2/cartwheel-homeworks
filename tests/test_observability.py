"""HW2 authentication checks; no tracing service or live model required."""

import json
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from server import app as server_app


@pytest.fixture
def client(world, tmp_path, monkeypatch):
    monkeypatch.setattr(server_app, "_SESSIONS", {})
    monkeypatch.setattr(server_app, "SESSIONS_DB", tmp_path / "sessions.db")
    # Avoid the application lifespan, which configures external tracing.
    return TestClient(server_app.app)


def test_session_rejects_claimed_role_mismatch(client):
    response = client.post("/sessions", json={"user_id": 1, "role": "support"})

    assert response.status_code == 403
    assert server_app._SESSIONS == {}


def test_token_cannot_authorize_another_session(client, monkeypatch):
    runner = AsyncMock()
    monkeypatch.setattr(server_app.Runner, "run", runner)
    first = client.post("/sessions", json={"user_id": 1, "role": "shopper"})
    second = client.post("/sessions", json={"user_id": 1, "role": "shopper"})
    assert first.status_code == second.status_code == 200
    first_session, second_session = first.json(), second.json()
    assert first_session["session_id"] != second_session["session_id"]

    response = client.post(
        f"/sessions/{second_session['session_id']}/messages",
        headers={"Authorization": f"Bearer {first_session['token']}"},
        json={"message": "Show my recent orders."},
    )

    assert response.status_code == 403
    runner.assert_not_called()


@pytest.mark.parametrize("capture_content", [True, False])
def test_generation_records_usage_and_respects_content_capture(capture_content):
    from agents import GenerationSpanData
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
    from observability.instrument import _record_generation_attributes

    provider = TracerProvider()
    exporter = InMemorySpanExporter()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    data = GenerationSpanData(
        model="ollama_chat/llama3.1:8b",
        output=[{"role": "assistant", "content": "Checking your order.", "tool_calls": [
            {"id": "call-1", "function": {"name": "get_order", "arguments": '{"order_id":4127}'}}
        ]}],
        usage={"input_tokens": 57, "output_tokens": 13, "total_tokens": 70},
    )
    try:
        with provider.get_tracer(__name__).start_as_current_span("model") as span:
            _record_generation_attributes(span, data, capture_content)
        attributes = exporter.get_finished_spans()[0].attributes
        assert attributes["gen_ai.usage.input_tokens"] == 57
        assert attributes["gen_ai.usage.output_tokens"] == 13
        assert attributes["gen_ai.usage.total_tokens"] == 70
        assert attributes["gen_ai.provider.name"] == "ollama"
        if capture_content:
            parts = json.loads(attributes["gen_ai.output.messages"])[0]["parts"]
            assert parts[0] == {"type": "text", "content": "Checking your order."}
            assert parts[1]["name"] == "get_order"
            assert parts[1]["arguments"] == {"order_id": 4127}
        else:
            assert "gen_ai.output.messages" not in attributes
    finally:
        provider.shutdown()
