import pytest


@pytest.mark.asyncio
async def test_ask_empty_question_returns_422(client):
    response = await client.post("/api/ask", json={"question": ""})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_ask_too_long_question_returns_422(client):
    response = await client.post("/api/ask", json={"question": "a" * 2001})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_ask_missing_body_returns_422(client):
    response = await client.post("/api/ask", json={})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_ask_success(client, mock_embeddings, mock_search, mock_agent):
    response = await client.post(
        "/api/ask",
        json={"question": "Сколько стоит доставка?"},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["answer"] == "Тестовый ответ"
    assert data["agent"] == "qa_agent"
    assert isinstance(data["latency_ms"], (int, float))

    assert len(data["sources"]) == 1
    src = data["sources"][0]
    assert src["title"] == "delivery"
    assert src["score"] == 0.9


@pytest.mark.asyncio
async def test_ask_agent_failure_returns_fallback(
    client, mock_embeddings, mock_search, monkeypatch
):
    from app.api import routes as api_routes

    async def broken_agent(_q, _c):
        raise RuntimeError("LLM died")

    monkeypatch.setattr(api_routes, "generate_answer", broken_agent)

    response = await client.post("/api/ask", json={"question": "Тест"})
    assert response.status_code == 200
    data = response.json()
    assert data["agent"] == "fallback"
