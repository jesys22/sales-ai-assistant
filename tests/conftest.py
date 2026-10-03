import sys
from pathlib import Path
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.api import routes as api_routes  # noqa: E402
from app.db.session import get_session  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture
def mock_session():
    """Мок AsyncSession — не ходит в реальную БД."""
    return AsyncMock()


@pytest.fixture
def mock_embeddings(monkeypatch):
    """Подменяет embed_query — возвращает нулевой вектор."""
    def fake_embed_query(_query: str) -> list[float]:
        return [0.0] * 1024

    monkeypatch.setattr(api_routes, "embed_query", fake_embed_query)


@pytest.fixture
def mock_search(monkeypatch):
    """Подменяет search_similar — возвращает 1 фейковый чанк."""
    async def fake_search(_session, _embedding, top_k: int = 5):
        return [
            {
                "id": "fake-uuid-1",
                "title": "delivery (part 1)",
                "content": "Доставка по Москве — 300 рублей.",
                "source": "data/docs/delivery.txt",
                "score": 0.9,
            }
        ]

    monkeypatch.setattr(api_routes, "search_similar", fake_search)


@pytest.fixture
def mock_agent(monkeypatch):
    """Подменяет generate_answer — не ходит в LM Studio."""
    async def fake_generate(_question: str, _context: str) -> str:
        return "Тестовый ответ"

    monkeypatch.setattr(api_routes, "generate_answer", fake_generate)


@pytest_asyncio.fixture
async def client(mock_session):
    """AsyncClient с подменённой сессией БД."""
    async def override_get_session():
        yield mock_session

    app.dependency_overrides[get_session] = override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
