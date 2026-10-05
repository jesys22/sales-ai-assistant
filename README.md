# Sales AI Assistant

![CI](https://github.com/jesys22/sales-ai-assistant/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.12-blue)
![Coverage](https://img.shields.io/badge/coverage-86%25-brightgreen)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-teal)
![pgvector](https://img.shields.io/badge/pgvector-cosine-green)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

RAG-ассистент для отдела продаж интернет-магазина. Отвечает на вопросы клиентов о товарах, доставке, оплате и возвратах, опираясь **только** на базу знаний компании. Каждый ответ возвращается вместе с источниками — можно проверить, откуда взят факт, а не верить модели на слово.

## Возможности

- 🧠 **Полный RAG-пайплайн** — чанкинг → эмбеддинги → векторный поиск → реранкинг → генерация
- 🔎 **Прозрачность** — ответ всегда сопровождается списком источников (`id`, заголовок, текст, релевантность)
- 🤖 **Локальная LLM** — Qwen 2.5 Coder 14B через OpenAI-совместимый API (LM Studio), данные не уходят в облако
- 🛡️ **Отказоустойчивость** — при сбое LLM отвечает дежурной фразой, не роняя запрос
- ✅ **Строгая валидация** — Pydantic-схемы, вопрос от 1 до 2000 символов
- 📝 **Наблюдаемость** — структурированные JSON-логи (structlog) + логирование каждого запроса
- 🧪 **CI** — Ruff + Mypy + Pytest с замером покрытия на каждый push
- 🐳 **Инфраструктура** — PostgreSQL + pgvector через Docker Compose, миграции Alembic

## Архитектура

```
Клиент (браузер / curl)
        │  POST /api/ask  {"question": "…"}
        ▼
┌───────────────────────────────────────────────────┐
│                    FastAPI                        │
│                                                   │
│  1. embed_query(question)                        │
│     multilingual-e5-large → вектор (1024)        │
│         │                                         │
│  2. search_similar  (pgvector, cosine_distance)  │
│     → top-5 кандидатов                            │
│         │                                         │
│  3. rerank_by_keywords  → top-3                  │
│         │                                         │
│  4. контекст = [заголовок + текст] × 3           │
│         │                                         │
│  5. generate_answer  (Qwen 2.5 Coder, LM Studio) │
│     → ответ строго по контексту                  │
└───────────────────────────────────────────────────┘
        │
        ▼
{ answer, sources[], agent, latency_ms }
```

## Стек

| Слой | Технологии |
|---|---|
| Веб-фреймворк | FastAPI, Uvicorn |
| БД | PostgreSQL 16 + pgvector |
| ORM | SQLAlchemy 2.0 (async) |
| Миграции | Alembic |
| Эмбеддинги | sentence-transformers, `intfloat/multilingual-e5-large` (1024) |
| LLM | Qwen 2.5 Coder 14B Instruct (локально, OpenAI-совместимый API) |
| Валидация | Pydantic v2 + pydantic-settings |
| Логирование | structlog (JSON) |
| Тесты | pytest + pytest-asyncio + httpx (ASGI) |
| Качество кода | Ruff, Mypy |
| Контейнеризация | Docker Compose |

## Структура проекта

```
sales-ai-assistant/
├── app/
│   ├── main.py              # Точка входа, middleware, CORS, healthcheck
│   ├── config.py            # Настройки через pydantic-settings (.env)
│   ├── schemas.py           # Pydantic-схемы запросов/ответов
│   ├── api/
│   │   ├── routes.py        # POST /api/ask
│   │   └── static/          # Веб-интерфейс (HTML/JS/CSS)
│   ├── agents/
│   │   └── qa_agent.py      # Генерация ответа локальной LLM
│   ├── db/
│   │   ├── models.py        # Conversation, Message, Document, Lead
│   │   └── session.py       # Async engine + session factory
│   └── rag/
│       ├── chunking.py      # Разбиение текста на чанки
│       ├── embeddings.py    # Эмбеддинги e5-large
│       └── retriever.py     # pgvector-поиск + реранкинг
├── data/docs/               # База знаний (.txt / .md)
├── migrations/              # Миграции Alembic
├── scripts/
│   ├── check_db.py          # Проверка подключения к БД и pgvector
│   ├── index_documents.py   # Индексация документов в pgvector
│   └── test_search.py       # Ручная проверка поиска
├── tests/                   # 22 теста
├── docker-compose.yml       # PostgreSQL + pgvector
├── pyproject.toml           # Ruff, Mypy, Pytest
└── .github/workflows/ci.yml # CI
```

## Быстрый старт

### Требования

- Python 3.12+
- Docker (для PostgreSQL + pgvector)
- LM Studio с моделью `qwen2.5-coder-14b-instruct` (или любой OpenAI-совместимый сервер)

### 1. Установка

```bash
git clone https://github.com/jesys22/sales-ai-assistant.git
cd sales-ai-assistant
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### 2. Конфигурация

```bash
copy .env.example .env        # Windows
cp .env.example .env          # Linux / macOS
```

### 3. PostgreSQL + pgvector

```bash
docker-compose up -d
```

> ⚠️ **Порт.** Контейнер слушает **5433** на хосте (внутри — 5432). Поэтому в `.env` укажи:
>
> ```ini
> DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/sales_ai
> ```
>
> Если у тебя собственный PostgreSQL на стандартном `5432` — оставь значение по умолчанию.

### 4. Миграции

```bash
alembic upgrade head
```

### 5. Индексация базы знаний

Положи документы в `data/docs/` (`.txt` / `.md`) и запусти:

```bash
python scripts/index_documents.py
```

### 6. Запуск

```bash
uvicorn app.main:app --reload
```

Открой http://127.0.0.1:8000 — там веб-интерфейс.

### 7. Проверка

```bash
curl http://127.0.0.1:8000/health

curl -X POST http://127.0.0.1:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Сколько стоит доставка в Москву?"}'
```

## API

### `POST /api/ask`

**Запрос**

```json
{ "question": "Сколько стоит доставка в Москву?" }
```

**Ответ**

```json
{
  "answer": "Доставка по Москве — 300 рублей, срок 1–2 дня.",
  "sources": [
    {
      "id": "9f0a1e2c-…",
      "title": "delivery",
      "content": "Доставка по Москве — 300 рублей…",
      "score": 0.9
    }
  ],
  "agent": "qa_agent",
  "latency_ms": 145.2
}
```

Валидация: `question` — обязательная строка от 1 до 2000 символов, иначе `422`.

### `GET /health`

```json
{ "status": "ok" }
```

## Как работает RAG

1. **Чанкинг** (`app/rag/chunking.py`) — документ режется на смысловые куски по предложениям: `chunk_size=800`, `overlap=100`.
2. **Эмбеддинги** (`app/rag/embeddings.py`) — модель `intfloat/multilingual-e5-large` (1024 измерения), с префиксами `query:` / `passage:` и нормализацией.
3. **Векторный поиск** (`app/rag/retriever.py`) — `cosine_distance` в pgvector, top-5 кандидатов.
4. **Реранкинг** (`app/rag/retriever.py`) — пересечение ключевых слов запроса и текста чанка, top-3.
5. **Генерация** (`app/agents/qa_agent.py`) — топ-3 чанка собираются в контекст, Qwen 2.5 Coder отвечает строго по контексту (`temperature=0.2`). Если ответа нет в базе — честно говорит «Уточню информацию у коллег», а не выдумывает.

## Конфигурация

| Переменная | По умолчанию | Назначение |
|---|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://postgres:postgres@localhost:5432/sales_ai` | строка подключения |
| `QWEN_BASE_URL` | `http://127.0.0.1:1234/v1` | адрес OpenAI-совместимого сервера |
| `QWEN_MODEL` | `qwen2.5-coder-14b-instruct` | имя модели |
| `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` | — | (опционально) облачные LLM |
| `TELEGRAM_BOT_TOKEN` | — | задел под Telegram-бота |
| `BITRIX24_WEBHOOK_URL` | — | задел под интеграцию с Bitrix24 |
| `APP_ENV` / `LOG_LEVEL` | `dev` / `INFO` | окружение и уровень логов |

## Тестирование

**22 теста, покрытие ~86%.** Тесты не требуют реальной БД и LLM — БД, эмбеддинги, поиск и генерация подменяются моками (`pytest` + `monkeypatch` + `ASGITransport`).

```bash
pytest
```

## 📊 Качество RAG (benchmark)

Оцениваю через собственный evaluator (`scripts/evaluate_rag.py`) на golden set из 20 вопросов.

| Метрика | Значение | Что показывает |
|---------|----------|----------------|
| **Semantic Similarity** | **0.97** | Косинусное сходство ответа RAG и эталонного ответа (e5-large) |
| **Keyword Recall** | **0.77** | Доля ключевых фактов из эталона, попавших в ответ |
| **Keyword Precision** | **0.78** | Отсутствие галлюцинаций: доля слов ответа, есть в эталоне |
| **Retrieval Hit Rate** | **0.95** | Доля вопросов, где правильный документ попал в top-5 |

**Golden set:** 20 вопросов, включая проверку на галлюцинации (вопросы вне базы знаний).

Запуск: `python scripts/evaluate_rag.py`

Покрывают: валидацию запросов (пустой / слишком длинный / отсутствующий), чанкинг (разбиение, overlap, загрузка файлов), реранкинг, Pydantic-схемы и fallback-агента при сбое LLM.

## CI

На каждый push и pull request (`.github/workflows/ci.yml`):

- **Ruff** — линтер
- **Mypy** — проверка типов
- **Pytest** — тесты + замер покрытия, выгрузка в Codecov

## Дорожная карта (задел на будущее)

Схема БД и конфиг уже содержат заготовки под расширение — это осознанный фундамент, а не реализованный функционал:

- **Telegram-бот** — `TELEGRAM_BOT_TOKEN` в конфиге
- **CRM Bitrix24** — `BITRIX24_WEBHOOK_URL` в конфиге
- **Метрики Prometheus** — `prometheus-client` в зависимостях (эндпоинт `/metrics` ещё не добавлен)
- **Мультиагентная оркестрация** — модели `Conversation` / `Message` / `Lead` уже в схеме БД

## Лицензия

[MIT](LICENSE)
