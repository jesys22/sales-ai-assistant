import time
import uuid

import structlog
from fastapi import APIRouter

from app.schemas import AskRequest, AskResponse

router = APIRouter()
logger = structlog.get_logger()


@router.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest) -> AskResponse:
    request_id = str(uuid.uuid4())
    start = time.perf_counter()

    logger.info(
        "ask_request",
        request_id=request_id,
        question=request.question[:100],
    )

    # Заглушка — заменим позже на RAG + агентов
    answer = f"Echo: {request.question}"
    latency_ms = (time.perf_counter() - start) * 1000

    return AskResponse(
        answer=answer,
        sources=[],
        agent="stub",
        latency_ms=round(latency_ms, 2),
    )