# Import necessary libraries and functions
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import structlog
from contextlib import asynccontextmanager
def get_settings():
    from app.config import Settings
    return Settings()

# Configure structlog to use JSON format and log level from settings
logger = structlog.get_logger()
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt='iso'),
        structlog.processors.JSONRenderer(),
    ],
)

app = FastAPI(title="Sales AI Assistant", version="0.1.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lifespan hook for logging application start and stop
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application started")
    yield
    logger.info("Application stopped")

app.lifespan = lifespan

# Middleware to log incoming requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    logger.info(
        "HTTP request",
        method=request.method,
        path=request.url.path,
        duration=process_time,
    )
    return response

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok"}