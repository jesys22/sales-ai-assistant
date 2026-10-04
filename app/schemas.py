from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)


class SourceItem(BaseModel):
    id: str
    title: str
    content: str
    score: float


class AskResponse(BaseModel):
    answer: str
    sources: list[SourceItem] = []
    agent: str
    latency_ms: float
    confidence: float = 0.0


class HealthResponse(BaseModel):
    status: str


class LeadInfo(BaseModel):
    name: str | None = None
    contact: str | None = None
    status: str = "new"
    score: float = 0.0
