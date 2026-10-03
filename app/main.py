import time
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import router as api_router
from app.config import get_settings

settings = get_settings()

# Настройка structlog с JSON-форматом
structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ],
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application started", env=settings.app_env)
    yield
    logger.info("Application stopped")


app = FastAPI(
    title="Sales AI Assistant",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware для логирования запросов
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start_time) * 1000
    logger.info(
        "http_request",
        method=request.method,
        path=request.url.path,
        status=response.status_code,
        duration_ms=round(duration_ms, 2),
    )
    return response


# Health check
@app.get("/health")
async def health_check():
    return {"status": "ok"}


# API routes
app.include_router(api_router, prefix="/api", tags=["ask"])


# Раздача статики
app.mount("/static", StaticFiles(directory="static"), name="static")


# Корневой эндпоинт — отдаёт UI
@app.get("/", include_in_schema=False)
async def root():
    return FileResponse("static/index.html")
