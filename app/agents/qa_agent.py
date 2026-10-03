import httpx
import structlog

from app.config import get_settings

logger = structlog.get_logger()
settings = get_settings()


async def generate_answer(question: str, context: str) -> str:
    """Отправляет запрос в локальную Qwen через OpenAI-compatible API."""

    system_prompt = (
        "Ты AI-ассистент отдела продаж интернет-магазина. "
        "Отвечай кратко и по делу, используя ТОЛЬКО информацию из контекста ниже. "
        "Если ответа нет в контексте — скажи: 'Уточню информацию у коллег'. "
        "Не выдумывай.\n\n"
        f"Контекст:\n{context}"
    )

    payload = {
        "model": settings.qwen_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
        "temperature": 0.2,
        "max_tokens": 400,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{settings.qwen_base_url}/chat/completions",
            json=payload,
        )
        response.raise_for_status()
        data = response.json()

    answer = data["choices"][0]["message"]["content"]
    logger.info(
        "qa_agent_answer",
        question=question[:80],
        answer_len=len(answer),
        prompt_tokens=data.get("usage", {}).get("prompt_tokens"),
    )
    return answer
