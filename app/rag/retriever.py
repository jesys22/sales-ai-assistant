import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Document

logger = structlog.get_logger()


async def search_similar(
    session: AsyncSession,
    query_embedding: list[float],
    top_k: int = 5,
) -> list[dict]:
    """Ищет top_k похожих документов через pgvector (cosine distance)."""
    distance = Document.embedding.cosine_distance(query_embedding)

    stmt = (
        select(
            Document.id,
            Document.title,
            Document.content,
            Document.source,
            distance.label("distance"),
        )
        .order_by(distance)
        .limit(top_k)
    )

    result = await session.execute(stmt)
    rows = result.all()

    return [
        {
            "id": str(row.id),
            "title": row.title,
            "content": row.content,
            "source": row.source,
            "score": round(1.0 - row.distance, 4),
        }
        for row in rows
    ]


def rerank_by_keywords(query: str, candidates: list[dict], top_n: int = 3) -> list[dict]:
    """Простейший реранкинг по пересечению слов."""
    query_words = {w.lower() for w in query.split() if len(w) > 2}

    def score(candidate: dict) -> float:
        text = candidate["content"].lower()
        hits = sum(1 for w in query_words if w in text)
        return hits / max(len(query_words), 1)

    ranked = sorted(candidates, key=score, reverse=True)
    return ranked[:top_n]
