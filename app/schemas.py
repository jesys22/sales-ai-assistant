from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)


class AskResponse(BaseModel):
    answer: str
    sources: list[str] = []
    agent: str
    latency_ms: float


class HealthResponse(BaseModel):
    status: str


class LeadInfo(BaseModel):
    name: str | None = None
    contact: str | None = None
    status: str = "new"
    score: float = 0.0