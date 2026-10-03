# Sales AI Assistant

![CI](https://github.com/jesys22/sales-ai-assistant/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.12-blue)
![Coverage](https://img.shields.io/badge/coverage-86%25-brightgreen)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-teal)

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
