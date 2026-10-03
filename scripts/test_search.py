import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db.session import async_session_maker, engine
from app.rag.embeddings import embed_query
from app.rag.retriever import rerank_by_keywords, search_similar


async def test():
    query = "Сколько стоит доставка в Москву?"
    print(f"Query: {query}")

    query_emb = embed_query(query)
    print(f"Query embedding dim: {len(query_emb)}")

    async with async_session_maker() as session:
        results = await search_similar(session, query_emb, top_k=3)

    print(f"\nFound {len(results)} candidates:")
    for r in results:
        print(f"  - [{r['score']}] {r['title']}")
        print(f"    {r['content'][:120]}...")

    reranked = rerank_by_keywords(query, results, top_n=2)
    print(f"\nAfter reranking (top 2):")
    for r in reranked:
        print(f"  - {r['title']} (score: {r['score']})")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(test())