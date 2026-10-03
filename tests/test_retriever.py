from app.rag.retriever import rerank_by_keywords


def test_rerank_sorts_by_relevance():
    candidates = [
        {"title": "a", "content": "доставка москва сроки", "score": 0.5},
        {"title": "b", "content": "оплата картой", "score": 0.6},
        {"title": "c", "content": "доставка", "score": 0.4},
    ]
    ranked = rerank_by_keywords("доставка москва", candidates, top_n=2)
    assert len(ranked) == 2
    assert ranked[0]["title"] == "a"


def test_rerank_empty_query():
    candidates = [{"title": "a", "content": "text", "score": 0.5}]
    ranked = rerank_by_keywords("", candidates, top_n=1)
    assert len(ranked) == 1


def test_rerank_short_words_ignored():
    candidates = [
        {"title": "a", "content": "доставка москва", "score": 0.5},
        {"title": "b", "content": "оплата", "score": 0.6},
    ]
    ranked = rerank_by_keywords("я и в", candidates, top_n=2)
    assert len(ranked) == 2


def test_rerank_limits_top_n():
    candidates = [{"title": f"t{i}", "content": "текст", "score": 0.5} for i in range(5)]
    ranked = rerank_by_keywords("текст", candidates, top_n=2)
    assert len(ranked) == 2