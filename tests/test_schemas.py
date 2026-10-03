import pytest
from pydantic import ValidationError

from app.schemas import AskRequest, AskResponse, SourceItem


def test_ask_request_valid():
    req = AskRequest(question="Привет")
    assert req.question == "Привет"


def test_ask_request_empty_raises():
    with pytest.raises(ValidationError):
        AskRequest(question="")


def test_ask_request_too_long_raises():
    with pytest.raises(ValidationError):
        AskRequest(question="a" * 2001)


def test_ask_response_default_sources():
    resp = AskResponse(answer="x", agent="y", latency_ms=1.0)
    assert resp.sources == []


def test_source_item_fields():
    src = SourceItem(id="1", title="delivery", content="text", score=0.85)
    assert src.score == 0.85
    assert src.title == "delivery"
