# Sales AI Assistant

AI-ассистент для отдела продаж с RAG, мультиагентной оркестрацией и интеграцией с CRM.

## Стек

- FastAPI + async SQLAlchemy 2.0
- PostgreSQL + pgvector
- Qwen 2.5 Coder 14B (локально через LM Studio)
- n8n для оркестрации
- Docker + GitHub Actions
- Prometheus + Grafana

## Быстрый старт

```bash
pip install -r requirements.txt
docker-compose up -d
uvicorn app.main:app --reload