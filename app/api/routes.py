import time
import uuid

import structlog
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.qa_agent import generate_answer
from app.db.session import get_session
from app.rag.embeddings import embed_query
from app.rag.retriever import rerank_by_keywords, search_similar
from app.schemas import AskRequest, AskResponse

router = APIRouter()
logger = structlog.get_logger()


@router.post("/ask", response_model=AskResponse)
async def ask(
    request: AskRequest,
    session: AsyncSession = Depends(get_session),
) -> AskResponse:
    request_id = str(uuid.uuid4())
    start = time.perf_counter()

    logger.info(
        "ask_request",
        request_id=request_id,
        question=request.question[:100],
    )

    # 1. Получаем embedding запроса
    query_emb = embed_query(request.question)

    # 2. Ищем top-5 похожих чанков через pgvector
    candidates = await search_similar(session, query_emb, top_k=5)

    # 3. Реранкинг: оставляем top-3
    top_chunks = rerank_by_keywords(request.question, candidates, top_n=3)

    # 4. Собираем контекст
    context = "\n\n".join(
        f"[{c['title']}]\n{c['content']}" for c in top_chunks
    )

    # 5. Генерируем ответ через Qwen
    try:
        answer = await generate_answer(request.question, context)
        agent_name = "qa_agent"
    except Exception as e:
        logger.error("qa_agent_failed", error=str(e), request_id=request_id)
        answer = "Извините, произошла ошибка. Уточню информацию у коллег."
        agent_name = "fallback"

    latency_ms = (time.perf_counter() - start) * 1000

    logger.info(
        "ask_response",
        request_id=request_id,
        latency_ms=round(latency_ms, 2),
        sources=[c["title"] for c in top_chunks],
    )

    return AskResponse(
        answer=answer,
        sources=[c["title"] for c in top_chunks],
        agent=agent_name,
        latency_ms=round(latency_ms, 2),
    )